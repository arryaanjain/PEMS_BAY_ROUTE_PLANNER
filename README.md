# 🚦 PeMS-Bay Traffic Dataset Loader & Inspector

This script downloads the **PeMS-Bay traffic dataset** from Google Drive, loads the sensor speed data and adjacency matrix, and prints basic info to verify successful extraction.

The dataset is commonly used for **traffic prediction research**, including models like **DCRNN, Graph WaveNet, ST-GCN**, etc.

---

## ✅ Features
- Downloads dataset directly from Google Drive  
- Loads `pems-bay.h5` traffic speed data  
- Loads adjacency matrix (`adj_mx_bay.pkl`)  
- Prints data shapes + sample slices  
- Ready as preprocessing step for GNN-based traffic forecasting

---

## 📦 Requirements
Install dependencies:

```bash
pip install pandas numpy h5py gdown
