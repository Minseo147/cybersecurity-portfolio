# 🔐 ML Privacy Risk Assessment using Membership Inference Attack (MIA)

> 이 프로젝트는 블랙박스 환경에서 Membership Inference Attack(MIA)을 수행하여  
> 머신러닝 모델의 프라이버시 침해 가능성을 정량적으로 평가합니다.  
> Shadow Model 기반 공격 전략과 ROC 기반 임계값 분석을 통해  
> 모델의 개인정보 유출 위험도를 분석하였습니다.

---

## 📌 1. Project Overview

This project evaluates privacy leakage risk in machine learning models  
using a **black-box Membership Inference Attack (MIA)** framework.

The objective is to determine whether an attacker can infer  
if a specific data sample was part of the model’s training dataset.

We implement:

- Multiple Shadow Models
- Siamese Neural Network architecture
- Confidence-based attack inference
- ROC curve analysis for threshold optimization
- Privacy risk level classification

---

## 🎯 2. Threat Model

**Adversary Capabilities:**
- Black-box access to target model
- Access to prediction confidence scores
- No access to model weights or training data

**Attack Goal:**
Determine whether a given sample was used in training.

---

## 🧠 3. Attack Methodology

### Step 1 — Train Shadow Models
Shadow models simulate the behavior of the target model using disjoint data splits.

### Step 2 — Collect Confidence Scores
Training samples (members) and test samples (non-members) are labeled.

### Step 3 — ROC-based Threshold Optimization
Optimal threshold selected using:

- ROC curve
- Youden’s J statistic (TPR − FPR)

### Step 4 — Apply Attack on Target Model
Multiple strategies tested:

- Mean threshold
- ROC optimal threshold
- Conservative threshold
- Aggressive threshold

---

## 📊 4. Privacy Risk Evaluation Metrics

- ROC AUC
- False Positive Rate (FPR)
- Overfitting Ratio
- Generalisation Gap
- High-confidence prediction rate

### Risk Classification Logic

| Worst FPR | Risk Level |
|-----------|------------|
| > 50%     | CRITICAL   |
| > 30%     | HIGH       |
| > 15%     | MODERATE   |
| > 5%      | LOW        |
| ≤ 5%      | MINIMAL    |

---

## 🏗 5. Model Architecture

### Shadow Model
- Siamese Autoencoder
- Contrastive loss
- Reconstruction regularization
- L1 activity regularization

### Attack Classifier
- MLP binary classifier
- Input: Embedding distance
- Output: Membership probability

---

## 📁 Project Structure
pprl-ml-privacy-risk-assessment/
│
├── attack_model/
│ ├── Attack Model ROC Curve.png
│ ├── Attack Result.png
│ ├── MIA_Attack_Final_v2.py
│ └── Δμ(top-1) result.png
│
├── report/
│ └── PPRL 기반 머신러닝 시스템의 프라이버시 리스크 평가 보고서
│
├── shadow_models/
│ ├── Shadow Models Performance Overview.png
│ ├── Shadow Models Training Log.png
│ └── Shadow_Final.py
│
├── target_model/
│ ├── Target Model Baseline Performance.png
│ └── confusion_matrix.png
│
└── README.md

> ⚠️ Dataset and trained model weights are excluded from this repository.

---

## 🔍 6. Key Findings

- Models with higher overfitting showed increased privacy leakage.
- High-confidence predictions correlate with membership inference vulnerability.
- Conservative threshold strategies significantly reduce false positive rates.
- ROC-based thresholding provides balanced attack performance.

---

## 🛡 7. Security Implications

This project demonstrates that:

- Overfitting increases privacy risk.
- Confidence scores expose leakage signals.
- Black-box attacks are feasible without internal model access.

Recommended Mitigations:

- Differential Privacy
- Confidence score clipping
- Regularization strengthening
- Calibration techniques

---

## 🚀 8. Technologies Used

- Python
- TensorFlow / Keras
- NumPy / Pandas
- scikit-learn
- Matplotlib

---

## 📌 9. Author Note

This project was implemented as part of an AI privacy risk assessment study.  
It demonstrates practical attack modeling and privacy evaluation techniques.

