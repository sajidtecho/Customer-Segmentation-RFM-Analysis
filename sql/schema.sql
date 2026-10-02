-- MySQL Schema for Customer Segmentation & RFM Analytics Project
CREATE DATABASE IF NOT EXISTS ecom_rfm_db;
USE ecom_rfm_db;

-- 1. Raw Transactions Table
DROP TABLE IF EXISTS raw_transactions;
CREATE TABLE raw_transactions (
    InvoiceNo VARCHAR(50),
    StockCode VARCHAR(50),
    Description VARCHAR(255),
    Quantity INT,
    InvoiceDate DATETIME,
    UnitPrice DECIMAL(10, 2),
    CustomerID INT,
    Country VARCHAR(100)
);

-- 2. Cleaned Transactions Table
DROP TABLE IF EXISTS cleaned_transactions;
CREATE TABLE cleaned_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    InvoiceNo VARCHAR(50) NOT NULL,
    StockCode VARCHAR(50) NOT NULL,
    Description VARCHAR(255),
    Quantity INT NOT NULL,
    InvoiceDate DATETIME NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    Revenue DECIMAL(12, 2) NOT NULL,
    CustomerID INT NOT NULL,
    Country VARCHAR(100) NOT NULL,
    InvoiceYear INT,
    InvoiceMonth INT,
    InvoiceDay INT,
    InvoiceHour INT,
    InvoiceMonthYear VARCHAR(7),
    INDEX idx_customer (CustomerID),
    INDEX idx_invoicedate (InvoiceDate),
    INDEX idx_invoiceno (InvoiceNo)
);

-- 3. Customer RFM & Segmentation Table
DROP TABLE IF EXISTS customer_segments;
CREATE TABLE customer_segments (
    CustomerID INT PRIMARY KEY,
    Recency INT NOT NULL,
    Frequency INT NOT NULL,
    Monetary DECIMAL(12, 2) NOT NULL,
    R_Score INT NOT NULL,
    F_Score INT NOT NULL,
    M_Score INT NOT NULL,
    RFM_Score VARCHAR(10) NOT NULL,
    RFM_Total_Score INT NOT NULL,
    Segment VARCHAR(50) NOT NULL,
    Cluster INT,
    Cluster_Label VARCHAR(50),
    INDEX idx_segment (Segment),
    INDEX idx_cluster (Cluster)
);
