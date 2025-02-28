# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 19:38:34 2025

@author: gov97
"""

import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Suppress warnings
import warnings 
warnings.filterwarnings('ignore')
sns.set(style='ticks')

# Define the root directory containing disease folders
data_root = "./"  # Adjust the path as needed

def get_disease_folders(root_dir):
    return [f for f in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, f))]

def get_descriptor_files(disease_folder):
    folder_path = os.path.join(data_root, disease_folder)
    return [f for f in os.listdir(folder_path) if "descriptor" in f.lower() and f.endswith(".csv")]

# Streamlit UI
st.title("Bioactivity of Target Protein")

# Step 1: Select Disease
folders = get_disease_folders(data_root)
folders=folders[1:]
disease = st.selectbox("Select a Disease", folders)

if disease:
    # Step 2: Select Descriptor File
    descriptor_files = get_descriptor_files(disease)
    filename = st.selectbox("Select a Descriptor File", descriptor_files)
    
    if filename:
        file_path = os.path.join(data_root, disease, filename)
        dataset = pd.read_csv(file_path)
        
        # Data Preprocessing
        dataset.rename(columns={'Name': 'molecule_chembl_id'}, inplace=True)  
        dataset = dataset[dataset['pIC50'].notna()]
        dataset = dataset.drop(columns=['smiles'], errors='ignore')
        X = dataset.drop('pIC50', axis=1)
        Y = dataset['pIC50']
        
        # Feature Selection
        selection = VarianceThreshold(threshold=(.8 * (1 - .8)))    
        X = selection.fit_transform(X)
        
        # Train-Test Split
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        # Train Model
        model = RandomForestRegressor(n_estimators=41)
        model.fit(X_train, Y_train)
        
        # Evaluate Model
        r2 = model.score(X_test, Y_test)
        st.write(f"R-squared value: {r2:.4f}")
        
        # Predictions
        Y_pred = model.predict(X_test)
        
        # Plot
        fig, ax = plt.subplots()
        sns.regplot(x=Y_test, y=Y_pred, scatter_kws={'alpha': 0.4}, ax=ax)
        ax.set_xlabel('Experimental pIC50', fontsize='large', fontweight='bold')
        ax.set_ylabel('Predicted pIC50', fontsize='large', fontweight='bold')
        plt.grid()
        
        st.pyplot(fig)
