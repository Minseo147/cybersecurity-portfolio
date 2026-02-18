import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers, Input, Model
import warnings
import os
# Suppress warnings and TensorFlow messages
warnings.filterwarnings('ignore')
# Suppress TensorFlow info/warning messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

# =============================================================================
# DATA LOADING AND SPLITTING - Computational embedding split
# =============================================================================
NUM_SHADOW_MODELS = 6
BASE_PATH = "./data/embeddings"
OUTPUT_DIR = "./outputs"

X1_TRAIN_PATH = f"{BASE_PATH}/x1_shadow_train.npy"
X2_TRAIN_PATH = f"{BASE_PATH}/x2_shadow_train.npy"
Y_TRAIN_PATH = f"{BASE_PATH}/y_shadow_train.npy"
X1_TEST_PATH = f"{BASE_PATH}/x1_shadow_test.npy"
X2_TEST_PATH = f"{BASE_PATH}/x2_shadow_test.npy"
Y_TEST_PATH = f"{BASE_PATH}/y_shadow_test.npy"

SHADOW_TRAIN_PATH = f"{BASE_PATH}/shadow_train.csv"
SHADOW_TEST_PATH = f"{BASE_PATH}/shadow_test.csv"

print(f"=== SHADOW MODEL {NUM_SHADOW_MODELS} TRAINING ===\n")
shadow_train_df = pd.read_csv(SHADOW_TRAIN_PATH)
shadow_test_df = pd.read_csv(SHADOW_TEST_PATH)

print("Loading complete shadow embeddings for splitting...")
x1_train_full = np.load(X1_TRAIN_PATH)
x2_train_full = np.load(X2_TRAIN_PATH)
y_train_full = np.load(Y_TRAIN_PATH)
x1_test_full = np.load(X1_TEST_PATH)
x2_test_full = np.load(X2_TEST_PATH)
y_test_full = np.load(Y_TEST_PATH)


def split_data_for_shadow_models(x1_train_full, x2_train_full, y_train_full, x1_test_full, x2_test_full, y_test_full, shadow_train_df, shadow_test_df, num_models):
    # Calculate equal split sizes
    train_split_size = len(y_train_full) // num_models
    test_split_size = len(y_test_full) // num_models

    # Calculate total usable samples
    total_train_used = train_split_size * num_models
    total_test_used = test_split_size * num_models

    print(f"\nData splitting strategy:")
    print(f"Train samples per shadow: {train_split_size}")
    print(f"Test samples per shadow: {test_split_size}")
    print(f"Train samples discarded: {len(y_train_full) - total_train_used}")
    print(f"Test samples discarded: {len(y_test_full) - total_test_used}")

    shadow_datasets = []
    for model_idx in range(num_models):
        # Calculate start and end indices for this shadow model
        train_start = model_idx * train_split_size
        train_end = (model_idx + 1) * train_split_size
        test_start = model_idx * test_split_size
        test_end = (model_idx + 1) * test_split_size

        # Extract data for this shadow model
        x1_train = x1_train_full[train_start:train_end]
        x2_train = x2_train_full[train_start:train_end]
        y_train = y_train_full[train_start:train_end]
        x1_test = x1_test_full[test_start:test_end]
        x2_test = x2_test_full[test_start:test_end]
        y_test = y_test_full[test_start:test_end]

        train_df = shadow_train_df.iloc[train_start:train_end].copy()
        test_df = shadow_test_df.iloc[test_start:test_end].copy()

        shadow_datasets.append(
            (x1_train, x2_train, y_train, x1_test, x2_test, y_test, train_df, test_df))
        print(
            f"  Shadow {model_idx + 1}: Train[{train_start}:{train_end}], Test[{test_start}:{test_end}]")

    return shadow_datasets


# CALL: Split data for all shadow models
shadow_datasets = split_data_for_shadow_models(x1_train_full, x2_train_full, y_train_full, x1_test_full, x2_test_full, y_test_full,
                                               shadow_train_df, shadow_test_df, NUM_SHADOW_MODELS)


def calculate_overfitting(model, x_train, y_train, x_val, y_val):
    train_loss = model.evaluate(x_train, y_train, verbose=0)
    val_loss = model.evaluate(x_val, y_val, verbose=0)

    if isinstance(train_loss, list):
        train_loss, train_acc = train_loss[0], train_loss[1]
        val_loss, val_acc = val_loss[0], val_loss[1]
    else:
        train_acc = val_acc = None

    overfitting_ratio = val_loss / \
        train_loss if train_loss > 0 else float('inf')
    generalisation_gap = val_loss - train_loss

    metrics = {
        'train_loss': train_loss,
        'val_loss': val_loss,
        'overfitting_ratio': overfitting_ratio,
        'generalisation_gap': generalisation_gap
    }
    if train_acc is not None and val_acc is not None:
        acc_gap = train_acc - val_acc
        metrics.update({
            'train_acc': train_acc,
            'val_acc': val_acc,
            'accuracy_gap': acc_gap
        })

    return metrics

# =============================================================================
# SHADOW MODEL PIPELINE
# =============================================================================


class ShadowModel:
    def __init__(self, embedding_dim):
        self.embedding_dim = embedding_dim
        self.build_snn_model()

    def build_snn_model(self):
        encoder_input = Input(shape=(self.embedding_dim,))
        x = layers.Dense(50, activity_regularizer=regularizers.l1(0.01))(
            encoder_input)
        x = layers.LeakyReLU(alpha=0.01)(x)
        encoder_output = layers.Dense(self.embedding_dim)(x)
        self.encoder = Model(encoder_input, encoder_output)

        decoder_input = Input(shape=(self.embedding_dim,))
        decoder_output = layers.Dense(
            self.embedding_dim, activation='sigmoid')(decoder_input)
        self.decoder = Model(decoder_input, decoder_output)

        input1 = Input(shape=(self.embedding_dim,))
        input2 = Input(shape=(self.embedding_dim,))
        encoded1 = self.encoder(input1)
        encoded2 = self.encoder(input2)
        recon1 = self.decoder(encoded1)
        recon2 = self.decoder(encoded2)

        merged_output = layers.Concatenate()(
            [encoded1, encoded2, recon1, recon2])
        self.siamese_model = Model(
            inputs=[input1, input2], outputs=merged_output)

        # Classification head
        input_diff = Input(shape=(self.embedding_dim,))
        x = layers.Dense(64, activation='relu')(input_diff)
        x = layers.Dense(32, activation='relu')(x)
        output = layers.Dense(1, activation='sigmoid')(x)
        self.classifier = Model(inputs=input_diff, outputs=output)

    def hybrid_classification_loss(self, margin=2.5, alpha=1.0):
        def loss_fn(y_true, y_pred):
            emb_dim = tf.shape(y_pred)[1] // 4
            encoded1 = y_pred[:, :emb_dim]
            encoded2 = y_pred[:, emb_dim:2*emb_dim]
            recon1 = y_pred[:, 2*emb_dim:3*emb_dim]
            recon2 = y_pred[:, 3*emb_dim:]

            # Contrastive loss on encoded vectors
            distances = tf.norm(encoded1 - encoded2, axis=1)
            y_true = tf.cast(y_true, tf.float32)
            contrastive_loss = y_true * \
                tf.square(distances) + (1 - y_true) * \
                tf.square(tf.maximum(margin - distances, 0))

            # Reconstruction loss: input vs reconstruction
            recon_loss1 = tf.reduce_mean(tf.square(encoded1 - recon1), axis=1)
            recon_loss2 = tf.reduce_mean(tf.square(encoded2 - recon2), axis=1)
            recon_loss = 0.5 * (recon_loss1 + recon_loss2)

            return tf.reduce_mean(alpha * recon_loss + contrastive_loss)
        return loss_fn

    def train_model(self, x1_train, x2_train, y_train, x1_test, x2_test, y_test):
        print(f"\nTraining shadow model")
        self.siamese_model.compile(
            optimizer='adam', loss=self.hybrid_classification_loss(margin=2.5, alpha=1.0))
        self.siamese_model.fit([x1_train, x2_train], y_train, epochs=30,
                               batch_size=256, validation_split=0.1, verbose=0)

        print("Siamese autoencoder training completed")
        val_split = int(0.9 * len(x1_train))
        x1_train_sub, x1_val = x1_train[:val_split], x1_train[val_split:]
        x2_train_sub, x2_val = x2_train[:val_split], x2_train[val_split:]
        y_train_sub, y_val = y_train[:val_split], y_train[val_split:]
        siamese_metrics = calculate_overfitting(self.siamese_model, [
                                                x1_train_sub, x2_train_sub], y_train_sub, [x1_val, x2_val], y_val)

        print("Siamese model overfitting metrics calculated")
        encoded1_train = self.encoder.predict(x1_train, verbose=0)
        encoded2_train = self.encoder.predict(x2_train, verbose=0)
        encoded1_test = self.encoder.predict(x1_test, verbose=0)
        encoded2_test = self.encoder.predict(x2_test, verbose=0)

        diff_train = np.abs(encoded1_train - encoded2_train)
        diff_test = np.abs(encoded1_test - encoded2_test)

        # Train classifier
        self.classifier.compile(
            optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        self.classifier.fit(diff_train, y_train, epochs=20,
                            batch_size=256, validation_split=0.1, verbose=0)
        print("Classifier training completed")

        diff_train_sub, diff_val = diff_train[:
                                              val_split], diff_train[val_split:]
        classifier_metrics = calculate_overfitting(
            self.classifier,
            diff_train_sub, y_train_sub,
            diff_val, y_val
        )
        self.overfitting_metrics = {
            'siamese': siamese_metrics,
            'classifier': classifier_metrics
        }

        return diff_train, diff_test

    # Generate predictions with UID information and membership labels
    def generate_combined_predictions_with_uids(self, diff_train, diff_test, y_train, y_test, shadow_train_df, shadow_test_df):
        y_train_pred_prob = self.classifier.predict(
            diff_train, verbose=0).flatten()
        y_train_pred = (y_train_pred_prob >= 0.5).astype(int)

        y_test_pred_prob = self.classifier.predict(
            diff_test, verbose=0).flatten()
        y_test_pred = (y_test_pred_prob >= 0.5).astype(int)

        combined_predictions = []
        # Add training predictions
        for i, (true_label, pred_label, confidence) in enumerate(zip(y_train, y_train_pred, y_train_pred_prob)):
            train_row = shadow_train_df.iloc[i]
            combined_predictions.append({
                'uid1': train_row['uid1'],
                'uid2': train_row['uid2'],
                'True Label': int(true_label),
                'Predicted Label': int(pred_label),
                'Confidence': float(confidence),
                'Is_Member': 1  # Training data = member
            })

        # Add test predictions
        for i, (true_label, pred_label, confidence) in enumerate(zip(y_test, y_test_pred, y_test_pred_prob)):
            test_row = shadow_test_df.iloc[i]
            combined_predictions.append({
                'uid1': test_row['uid1'],
                'uid2': test_row['uid2'],
                'True Label': int(true_label),
                'Predicted Label': int(pred_label),
                'Confidence': float(confidence),
                'Is_Member': 0  # Test data = non-member
            })

        return combined_predictions


# =============================================================================
# MAIN EXECUTION
# =============================================================================
embedding_dim = x1_train_full.shape[1]
all_results = []
for shadow_idx in range(NUM_SHADOW_MODELS):
    shadow_id = shadow_idx + 1  # indexed for display only

    print(f"\n{'='*70}")
    print(f"SHADOW MODEL {shadow_id}/{NUM_SHADOW_MODELS}")
    print(f"{'='*70}")
    x1_train, x2_train, y_train, x1_test, x2_test, y_test, shadow_train_df, shadow_test_df = shadow_datasets[
        shadow_idx]

    print(f"\nData alignment check:")
    print(
        f"  Embedding train: {len(y_train)}, CSV train: {len(shadow_train_df)}")
    print(f"  Embedding test: {len(y_test)}, CSV test: {len(shadow_test_df)}")

    if len(y_train) != len(shadow_train_df) or len(y_test) != len(shadow_test_df):
        print(f"WARNING: Size mismatch detected! Using minimum size.")
        min_train = min(len(y_train), len(shadow_train_df))
        min_test = min(len(y_test), len(shadow_test_df))

        x1_train = x1_train[:min_train]
        x2_train = x2_train[:min_train]
        y_train = y_train[:min_train]
        shadow_train_df = shadow_train_df.iloc[:min_train]

        x1_test = x1_test[:min_test]
        x2_test = x2_test[:min_test]
        y_test = y_test[:min_test]
        shadow_test_df = shadow_test_df.iloc[:min_test]
    else:
        print("Data aligned correctly")

    # CALL: Train shadow model
    shadow_model = ShadowModel(embedding_dim)
    diff_train, diff_test = shadow_model.train_model(
        x1_train, x2_train, y_train, x1_test, x2_test, y_test)

    # CALL: Generate predictions
    combined_predictions = shadow_model.generate_combined_predictions_with_uids(
        diff_train, diff_test, y_train, y_test, shadow_train_df, shadow_test_df)

    output_path = f"{OUTPUT_DIR}/Shadow{shadow_id}_predictions.csv"
    pd.DataFrame(combined_predictions).to_csv(output_path, index=False)

    # Calculate accuracies
    train_acc = sum(1 for i, pred in enumerate(combined_predictions[:len(y_train)])
                    if pred['True Label'] == pred['Predicted Label']) / len(y_train)
    test_acc = sum(1 for i, pred in enumerate(combined_predictions[len(y_train):])
                   if pred['True Label'] == pred['Predicted Label']) / len(y_test)

    # PRINT: metric output per run
    print(f"\n--- SHADOW MODEL {shadow_id} RESULTS ---")
    print(f"Predictions saved: {output_path}")
    print(f"Total predictions: {len(combined_predictions)}")
    print(
        f"  - Training samples (members): {sum(1 for p in combined_predictions if p['Is_Member'] == 1)}")
    print(
        f"  - Test samples (non-members): {sum(1 for p in combined_predictions if p['Is_Member'] == 0)}")
    print(f"\nModel Performance:")
    print(f"  - Training accuracy: {train_acc:.1%}")
    print(f"  - Test accuracy: {test_acc:.1%}")

    print(f"\n--- OVERFITTING ANALYSIS ---")
    print("Siamese Autoencoder:")
    siamese_metrics = shadow_model.overfitting_metrics['siamese']
    print(f"  - Train Loss: {siamese_metrics['train_loss']:.4f}")
    print(f"  - Val Loss: {siamese_metrics['val_loss']:.4f}")
    print(f"  - Overfitting Ratio: {siamese_metrics['overfitting_ratio']:.2f}")
    print(
        f"  - Generalisation Gap: {siamese_metrics['generalisation_gap']:.4f}")

    print("\nClassifier:")
    classifier_metrics = shadow_model.overfitting_metrics['classifier']
    print(f"  - Train Loss: {classifier_metrics['train_loss']:.4f}")
    print(f"  - Val Loss: {classifier_metrics['val_loss']:.4f}")
    print(f"  - Train Accuracy: {classifier_metrics['train_acc']:.1%}")
    print(f"  - Val Accuracy: {classifier_metrics['val_acc']:.1%}")
    print(
        f"  - Overfitting Ratio: {classifier_metrics['overfitting_ratio']:.2f}")
    print(f"  - Accuracy Gap: {classifier_metrics['accuracy_gap']:.1%}")
    print(
        f"  - Generalisation Gap: {classifier_metrics['generalisation_gap']:.4f}")

    print(f"\n✓ Shadow model {shadow_id} completed successfully!")
