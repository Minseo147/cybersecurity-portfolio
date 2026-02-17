import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# File paths
BASE_PATH = "./data/shadow_models"
SHADOW_FILES = [
    f"{BASE_PATH}/Shadow_1/Shadow1_combined_predictions.csv",
    f"{BASE_PATH}/Shadow_2/Shadow2_combined_predictions.csv",
    f"{BASE_PATH}/Shadow_3/Shadow3_combined_predictions.csv",
    f"{BASE_PATH}/Shadow_4/Shadow4_combined_predictions.csv",
    f"{BASE_PATH}/Shadow_5/Shadow5_combined_predictions.csv",
    f"{BASE_PATH}/Shadow_6/Shadow6_combined_predictions.csv",
]
TARGET_FILE = "./data/target/final_test_predictions.csv"


def membership_inference_attack():
    print("=== MEMBERSHIP INFERENCE ATTACK ===\n")

    # Load shadow model predictions
    shadow_files = SHADOW_FILES

    shadow_member_conf = []
    shadow_nonmember_conf = []

    for i, file_path in enumerate(shadow_files):
        df = pd.read_csv(file_path)
        members = df[df['Is_Member'] == 1]['Confidence'].values
        non_members = df[df['Is_Member'] == 0]['Confidence'].values

        shadow_member_conf.extend(members)
        shadow_nonmember_conf.extend(non_members)
        print(
            f"Shadow {i+1}: {len(members)} members, {len(non_members)} non-members")

    # Analyze shadow confidence distributions
    member_mean = np.mean(shadow_member_conf)
    nonmember_mean = np.mean(shadow_nonmember_conf)
    member_std = np.std(shadow_member_conf)
    nonmember_std = np.std(shadow_nonmember_conf)

    print(f"\nShadow Analysis:")
    print(f"Members: {member_mean:.4f} ± {member_std:.4f}")
    print(f"Non-members: {nonmember_mean:.4f} ± {nonmember_std:.4f}")
    print(f"Gap: {member_mean - nonmember_mean:.4f}")

    # Find optimal threshold using ROC
    shadow_conf = np.concatenate([shadow_member_conf, shadow_nonmember_conf])
    shadow_labels = np.concatenate(
        [np.ones(len(shadow_member_conf)), np.zeros(len(shadow_nonmember_conf))])

    fpr, tpr, thresholds = roc_curve(shadow_labels, shadow_conf)
    roc_auc = auc(fpr, tpr)

    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)
    optimal_threshold = thresholds[optimal_idx]

    print(f"\nROC AUC: {roc_auc:.4f}")
    print(f"Optimal threshold: {optimal_threshold:.4f}")

    # Plot ROC curve
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='blue', lw=2,
             label=f'ROC Curve (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='red', lw=2,
             linestyle='--', label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve for Shadow Model Membership Inference')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("roc_curve.png", dpi=300, bbox_inches='tight')
    plt.show()
    print("ROC curve saved to: roc_curve.png")

    # Define threshold strategies
    strategies = {
        'Mean': (member_mean + nonmember_mean) / 2,
        'ROC_Optimal': optimal_threshold,
        'Conservative': nonmember_mean + 2 * nonmember_std,
        'Aggressive': nonmember_mean + nonmember_std
    }

    # Load target test predictions
    target_df = pd.read_csv(TARGET_FILE)
    target_conf = target_df['Confidence'].values

    print(f"\nTarget test data: {len(target_conf)} samples")
    print(
        f"Target confidence: {np.mean(target_conf):.4f} ± {np.std(target_conf):.4f}")

    # Apply attack strategies
    print(f"\nAttack Results:")
    results = {}

    for name, threshold in strategies.items():
        target_pred = (target_conf > threshold).astype(int)
        # Percentage of test data misclassified as training data
        fpr = np.mean(target_pred == 1)

        print(f"{name:12s}: {fpr:.1%} false positive rate")
        results[name] = fpr

    # Explain what these results mean
    print(f"\n# Understanding Attack Results:")
    print(f"# False Positive Rate = % of test data incorrectly identified as training data")
    print(f"# - Lower FPR = Better privacy protection")
    print(f"# - Higher FPR = Model vulnerable to membership inference")
    print(f"# - Random guessing would give ~50% FPR")

    # Privacy assessment
    worst_fpr = max(results.values())
    best_fpr = min(results.values())

    print(f"\nPrivacy Assessment:")
    print(
        f"Best FPR: {best_fpr:.1%}   # Best-case scenario (most conservative attack)")
    print(
        f"Worst FPR: {worst_fpr:.1%}  # Worst-case scenario (most aggressive attack)")

    if worst_fpr > 0.5:
        risk = "CRITICAL"
        explanation = "# Even aggressive attacks can identify >50% of test data as training data"
    elif worst_fpr > 0.3:
        risk = "HIGH"
        explanation = "# Significant vulnerability - attackers can identify substantial portions of training data"
    elif worst_fpr > 0.15:
        risk = "MODERATE"
        explanation = "# Some vulnerability present - limited but detectable privacy leakage"
    elif worst_fpr > 0.05:
        risk = "LOW"
        explanation = "# Minimal vulnerability - most test data correctly identified as non-training"
    else:
        risk = "MINIMAL"
        explanation = "# Good privacy protection - very low false identification rates"

    print(f"Risk Level: {risk}")
    print(explanation)

    # Check for overfitting indicators
    high_conf_rate = np.mean(target_conf > 0.8)
    print(f"\nOverfitting Check:")
    print(f"High confidence (>0.8) on test data: {high_conf_rate:.1%}")
    print(f"# This measures how often the model is very confident on unseen data")
    print(f"# Well-calibrated models should rarely be highly confident on test data")

    if high_conf_rate > 0.3:
        print("WARNING: High confidence on test data suggests overfitting")
        print("# This indicates the model may have memorized training patterns")
        print("# Creating vulnerability to membership inference attacks")

    return {
        'risk_level': risk,
        'best_fpr': best_fpr,
        'worst_fpr': worst_fpr,
        'roc_auc': roc_auc,
        'high_conf_rate': high_conf_rate
    }


# Run the attack
results = membership_inference_attack()
print(f"\n=== SUMMARY ===")
print(f"Privacy Risk: {results['risk_level']}")
print(f"Attack Success Rate: {results['worst_fpr']:.1%}")
