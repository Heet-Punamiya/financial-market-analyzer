# Comprehensive Study Guide for DMBI Viva

## Core Foundations of Your Subject (DMBI)
1. **Data Mining (KDD - Knowledge Discovery in Databases):** The process of discovering interesting, hidden, and useful patterns, correlations, and anomalies from large datasets. 
2. **Business Intelligence (BI):** The technologies and strategies used by enterprises for data analysis of business information. BI transforms raw data into meaningful insights to help businesses make better decisions (e.g., using dashboards in Power BI).
3. **Supervised vs. Unsupervised Learning:**
   * **Supervised:** The data has labels (e.g., predicting if an email is "Spam" or "Not Spam"). Used in Classification (like ID3).
   * **Unsupervised:** The data has no labels. The algorithm finds patterns on its own (e.g., grouping customers based on buying behavior). Used in Clustering (like K-Means).

---

## Assignment 2: Pivot Tables & Strategic Questions
**Concept:** Data Summarization.
* **What is a Pivot Table?** An interactive tool in Excel used to extract significance from a large, detailed data set. It allows you to aggregate (sum, average, count) data without writing complex formulas.
* **The 4 Quadrants:**
    1. **Rows:** Fields used to group data horizontally.
    2. **Columns:** Fields used to group data vertically.
    3. **Values:** The quantitative data you want to measure.
    4. **Filters:** Applies a condition to the entire table.
* **Viva Question:** *Why use a pivot table over normal formulas?*
    * **Answer:** Data abstraction, speed, flexibility (easy drag-and-drop), and avoiding human error associated with typing `SUMIFS` or `COUNTIFS`.

---

## Assignment 3: Power BI and Dashboards
**Concept:** Business Intelligence Visualization.
* **Concept Hierarchy (Drill-Down & Drill-Up):** 
    * **Hierarchy:** A logical arrangement of data. E.g., `Year -> Quarter -> Month -> Day`.
    * **Drill-Down:** Moving from a summary view to a detailed view.
    * **Drill-Up:** Moving from detailed data back to summary data.
* **Conditional Formatting:** Applying rules to change the color/style of data (e.g., Profit < $0 is marked Red).
* **Viva Question:** *What is the purpose of a dashboard?* 
    * **Answer:** To consolidate complex data into an easy-to-understand visual format, allowing stakeholders to make quick, data-driven business decisions.

---

## Assignment 4: Data Warehouse (DWH) Schema
**Concept:** Data Storage Architecture.
* **What is a Data Warehouse?** A central repository of integrated data from multiple sources used for reporting and analysis.
* **Schemas (Star vs. Snowflake):**
    * **Fact Table:** Sits at the center of the schema. Contains the quantitative, measurable data (e.g., `Sales_Amount`) and foreign keys to dimension tables.
    * **Dimension Table:** Surrounds the fact table. Contains descriptive attributes (e.g., `Time_Dim`, `Customer_Dim`).
* **Estimating Fact Table Size:** Number of records (rows) multiplied by the total size of one row in bytes.
* **Viva Question:** *What is the difference between a Fact and a Dimension?*
    * **Answer:** Facts are measurable metrics (numbers). Dimensions are the context or categories by which you analyze those facts (location, time).

---

## Assignment 5: Statistical Dispersion
**Concept:** Understanding Data Distribution.
* **Measures of Dispersion:**
    1. **Range:** Highest value minus lowest value. Sensitive to outliers.
    2. **Variance:** Average of squared differences from the Mean.
    3. **Standard Deviation:** The square root of Variance.
    4. **Interquartile Range (IQR):** Q3 - Q1. It represents the middle 50% of the data and is *not* affected by extreme outliers.
* **Box Plot:** A graph showing the Min, Q1, Median (Q2), Q3, and Max. Dots outside the whiskers are **Outliers** (calculated as data points below `Q1 - 1.5*IQR` or above `Q3 + 1.5*IQR`).

---

## Assignment 6: ID3 Algorithm (Iterative Dichotomiser 3)
**Concept:** Decision Tree Classification (Supervised Learning).
* **How it works:** It builds a decision tree from the top down. At each node, it evaluates which attribute best separates the data into distinct classes.
* **Entropy:** A measure of impurity, disorder, or randomness in the dataset. 
    * If all examples in a subset are positive (Pure), Entropy = 0.
    * If examples are exactly 50/50, Entropy = 1 (Maximum impurity).
* **Information Gain:** The reduction in Entropy achieved by splitting the data on a specific attribute. 
    * *Rule:* The algorithm calculates Information Gain for all available attributes and **chooses the attribute with the HIGHEST Information Gain** to be the root/decision node.
* **Viva Question:** *What is the stopping criteria for ID3?*
    * **Answer:** 1. All instances belong to the same class. 2. No more attributes left to split. 3. No more data left.

---

## Assignment 7: K-Means Clustering
**Concept:** Partitioning Clustering (Unsupervised Learning).
* **How it works:** 
    1. You choose the number of clusters (K).
    2. Algorithm randomly places K "Centroids" (cluster centers).
    3. Every data point is assigned to its nearest Centroid.
    4. Centroids move to the "mean" (average) of the points assigned to them.
    5. Repeat until Centroids stop moving.
* **Elbow Method:** How do you choose K? You run K-Means for K = 1, 2, 3... and calculate **WCSS (Within-Cluster Sum of Squares)**. You plot a graph of WCSS vs K. The point where the graph bends sharply (looks like an elbow) is your optimal K.
* **Viva Question:** *What is a drawback of K-Means?*
    * **Answer:** You have to manually define K beforehand, and it is highly sensitive to outliers and the initial random placement of centroids.

---

## Assignment 8: WEKA Tool & Association Rules
**Concept:** Using GUI Tools for Data Mining.
* **What is WEKA?** An open-source Java tool that provides a collection of ML algorithms via a GUI, eliminating the need to write code.
* **Key Tabs in WEKA:** Preprocess, Classify, Cluster, Associate.
* **Association Rule Mining (Apriori Algorithm):** Finds hidden rules like A -> B.
    * **Support:** How frequently the itemset appears in the database.
    * **Confidence:** How often the rule A -> B has been found to be true.

---

## Mini-Project: Credit Card Fraud Detection
**Concept:** Real-world Machine Learning Application.
* **The Problem:** The dataset is heavily **imbalanced**. Out of 284,807 transactions, only 492 are fraud.
* **The Solution (SMOTE):** Synthetic Minority Over-sampling Technique. It artificially generates new examples of the minority class (Fraud) so the dataset becomes 50-50.
* **Evaluation Metrics (Crucial):**
    * **Accuracy is bad here.**
    * **Recall (Sensitivity):** Out of all actual frauds, how many did we catch? *This is the most important metric for fraud detection because missing a fraud costs money.*
    * **Precision:** Out of all the ones we flagged as fraud, how many were actually fraud?
    * **F1-Score:** The harmonic mean of Precision and Recall.
