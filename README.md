# IntroPsych Confidence–Accuracy Study (CG vs EG)

## 📂 Repository Structure
```
IntroPsych/
│
├── data/
│   ├── raw/
│   │   └── Psychology Study Results.xlsx
│   └── processed/
│       └── study_results_clean.csv
│
├── src/
│   ├── cleaning.py
│   ├── scoring.py
│   └── stats.py
│
├── notebooks/
│   ├── 01_data_prep.ipynb
│   └── 02_analysis.ipynb
│
├── figures/
│   ├── accuracy_by_group.png
│   ├── abs_by_group.png
│   └── cws_by_group.png
│
├── requirements.txt
└── README.md
```

---

## 📘 Project Overview

This project analyses whether the **Control Group (CG)** and **Experimental Group (EG)** differ in:

- **Raw accuracy**
- **ABS confidence-weighted score**
- **CWS confidence-weighted score**

The full pipeline covers:

1. Cleaning and standardising the raw Excel responses  
2. Applying three scoring methods  
3. Running statistical tests (one-tailed t-tests)  
4. Generating figures and tables for reporting  

Everything is fully reproducible and version-controlled.

---

## 🧹 Data Cleaning

Run the cleaning pipeline:

```bash
python -m src.cleaning
```

This script:

- Loads both CG and EG Excel sheets  
- Extracts correctness (0/1) and confidence (1–7) for 20 questions  
- Removes non-participant rows  
- Generates columns: `correct_i`, `conf_i`, `p_i`, `abs_i`, `cws_i`  
- Computes participant-level totals  
- Saves the processed dataset to:

```
data/processed/study_results_clean.csv
```

---

## 🧮 Scoring Methods

### **1. Raw Accuracy**
Simple proportion of correct answers.

### **2. ABS Score (Augmented Brier-like scoring)**
A confidence-weighted scoring method based on absolute distance:

- High-confidence correct → strong reward  
- Guessed correct → moderate reward  
- Low-confidence incorrect → mild penalty  
- High-confidence incorrect → strong penalty  

Implemented in `scoring.py`.

### **3. CWS Score (Confidence-Weighted Scoring)**
A stricter scoring system emphasising calibration:

- Correct + high confidence → largest reward  
- Correct + low confidence → smaller reward  
- Incorrect + low confidence → minor penalty  
- Incorrect + high confidence → largest penalty  

Also implemented in `scoring.py`.

---

## 📊 Statistical Analysis

The notebook:

```
notebooks/02_analysis.ipynb
```

produces:

- Summary statistics  
- Histograms of accuracy, confidence, ABS, CWS  
- Group comparison barplots (with 95% CI)  
- One-tailed independent samples t-tests  
- Effect sizes (Cohen’s d)

Example output columns:

| score | CG mean | EG mean | t | p (one-tailed) | d |
|-------|---------|---------|---|----------------|---|

---

## 🎯 Hypothesis

- **H₁:** CG will perform better than EG (one-tailed)  
- **H₀:** No difference or EG performs equally/worse  

Analyses evaluate whether CG scores exceed EG scores across all three scoring methods.

---

## 📈 Figures

Figures are automatically saved to:

```
figures/
```

and include:

- `accuracy_by_group.png`
- `abs_by_group.png`
- `cws_by_group.png`

Each figure displays mean group scores with **95% CI error bars**.

---

## ▶️ Reproducibility Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Activate virtual environment

macOS / Linux:

```bash
source venv/bin/activate
```

### 3. Regenerate cleaned dataset

```bash
python -m src.cleaning
```

### 4. Run analysis notebooks

```bash
jupyter notebook
```

---

## 📝 Notes

- All data is from the class experiment and contains only participant names as originally collected.  
- Entire pipeline is deterministic and reproducible via `cleaning.py` + the analysis notebooks.  
- Figures and processed CSVs are automatically regenerated.

---