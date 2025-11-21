-- Create forex_trades table for HFM Assistant
-- Database: hfm_assistant
-- Table: forex_trades

-- Drop table if exists (optional - uncomment if you want to recreate)
-- DROP TABLE IF EXISTS forex_trades;

-- Create the forex_trades table
CREATE TABLE IF NOT EXISTS forex_trades (
    "Trade_ID" SERIAL PRIMARY KEY,
    "Trade_Date" DATE NOT NULL,
    "Symbol" VARCHAR(20) NOT NULL,
    "Trade_Type" VARCHAR(10) NOT NULL, -- 'Buy' or 'Sell'
    "Entry_Price" DECIMAL(10, 5) NOT NULL,
    "Exit_Price" DECIMAL(10, 5),
    "Lot_Size" DECIMAL(10, 2) NOT NULL,
    "Daily_PnL" DECIMAL(15, 2) NOT NULL,
    "Commission" DECIMAL(10, 2) DEFAULT 0.00,
    "Swap" DECIMAL(10, 2) DEFAULT 0.00,
    "Duration_Minutes" INTEGER,
    "Account_ID" VARCHAR(50),
    "Status" VARCHAR(20) DEFAULT 'Closed',
    "Notes" TEXT,
    "Created_At" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_trade_date ON forex_trades("Trade_Date");
CREATE INDEX IF NOT EXISTS idx_symbol ON forex_trades("Symbol");
CREATE INDEX IF NOT EXISTS idx_daily_pnl ON forex_trades("Daily_PnL");

-- Insert dummy data (100+ records with realistic forex trading data)
INSERT INTO forex_trades ("Trade_Date", "Symbol", "Trade_Type", "Entry_Price", "Exit_Price", "Lot_Size", "Daily_PnL", "Commission", "Swap", "Duration_Minutes", "Account_ID", "Status", "Notes")
VALUES
-- January 2024 - Mixed results
('2024-01-02', 'EUR/USD', 'Buy', 1.10500, 1.10650, 1.00, 150.00, -7.50, -2.30, 240, 'ACC001', 'Closed', 'Good momentum'),
('2024-01-02', 'GBP/USD', 'Sell', 1.27200, 1.27050, 0.50, 75.00, -5.00, -1.20, 180, 'ACC001', 'Closed', 'Breakout trade'),
('2024-01-03', 'USD/JPY', 'Buy', 144.50, 144.20, 1.50, -450.00, -10.00, -3.50, 360, 'ACC001', 'Closed', 'Stop loss hit'),
('2024-01-03', 'AUD/USD', 'Buy', 0.67800, 0.68100, 2.00, 600.00, -12.00, -4.00, 480, 'ACC001', 'Closed', 'Strong uptrend'),
('2024-01-04', 'EUR/GBP', 'Sell', 0.86500, 0.86300, 1.00, 200.00, -7.50, -2.00, 300, 'ACC001', 'Closed', 'Range trading'),
('2024-01-05', 'USD/CAD', 'Sell', 1.33200, 1.33500, 1.20, -360.00, -8.50, -2.80, 420, 'ACC001', 'Closed', 'News spike'),
('2024-01-08', 'NZD/USD', 'Buy', 0.62500, 0.62800, 1.50, 450.00, -10.00, -3.20, 360, 'ACC001', 'Closed', 'Clean setup'),
('2024-01-09', 'EUR/USD', 'Sell', 1.10800, 1.10950, 1.00, -150.00, -7.50, -2.00, 240, 'ACC001', 'Closed', 'False breakout'),
('2024-01-10', 'GBP/JPY', 'Buy', 183.50, 184.20, 0.80, 560.00, -6.00, -2.50, 300, 'ACC001', 'Closed', 'Volatility play'),
('2024-01-11', 'USD/CHF', 'Sell', 0.84500, 0.84200, 1.30, 390.00, -9.00, -3.00, 480, 'ACC001', 'Closed', 'Good risk/reward'),
('2024-01-12', 'EUR/USD', 'Buy', 1.09800, 1.10100, 2.00, 600.00, -12.00, -4.50, 360, 'ACC001', 'Closed', 'Trend continuation'),
('2024-01-15', 'AUD/CAD', 'Sell', 0.90200, 0.90500, 1.00, -300.00, -7.50, -2.20, 420, 'ACC001', 'Closed', 'Overextended'),
('2024-01-16', 'EUR/JPY', 'Buy', 159.80, 160.30, 1.20, 600.00, -8.50, -3.00, 300, 'ACC001', 'Closed', 'JPY weakness'),
('2024-01-17', 'GBP/USD', 'Buy', 1.27500, 1.27200, 1.50, -450.00, -10.00, -3.50, 480, 'ACC001', 'Closed', 'Wrong entry'),
('2024-01-18', 'USD/JPY', 'Sell', 145.20, 144.80, 1.00, 400.00, -7.50, -2.30, 240, 'ACC001', 'Closed', 'Perfect timing'),
('2024-01-19', 'NZD/JPY', 'Buy', 90.50, 91.20, 1.40, 980.00, -9.50, -3.50, 540, 'ACC001', 'Closed', 'Strong cross'),
('2024-01-22', 'EUR/USD', 'Sell', 1.09500, 1.09650, 1.00, -150.00, -7.50, -2.00, 180, 'ACC001', 'Closed', 'Market noise'),
('2024-01-23', 'CAD/JPY', 'Buy', 108.30, 108.90, 1.20, 720.00, -8.50, -3.00, 360, 'ACC001', 'Closed', 'Commodity boost'),
('2024-01-24', 'GBP/USD', 'Buy', 1.27800, 1.28200, 1.80, 720.00, -11.00, -4.00, 420, 'ACC001', 'Closed', 'BoE optimism'),
('2024-01-25', 'EUR/GBP', 'Sell', 0.85800, 0.85500, 1.50, 450.00, -10.00, -3.20, 300, 'ACC001', 'Closed', 'Divergence play'),
('2024-01-26', 'AUD/USD', 'Sell', 0.66500, 0.66800, 1.00, -300.00, -7.50, -2.50, 240, 'ACC001', 'Closed', 'Premature entry'),
('2024-01-29', 'USD/CAD', 'Buy', 1.34200, 1.34500, 1.30, 390.00, -9.00, -3.00, 360, 'ACC001', 'Closed', 'Oil impact'),
('2024-01-30', 'EUR/USD', 'Buy', 1.08200, 1.08600, 2.50, 1000.00, -14.00, -5.00, 480, 'ACC001', 'Closed', 'Big winner'),
('2024-01-31', 'GBP/JPY', 'Sell', 185.50, 185.80, 1.00, -300.00, -7.50, -2.30, 300, 'ACC001', 'Closed', 'Month-end volatility'),
('2024-02-01', 'EUR/USD', 'Buy', 1.08800, 1.09200, 2.00, 800.00, -12.00, -4.00, 360, 'ACC001', 'Closed', 'Strong start'),
('2024-02-02', 'USD/JPY', 'Sell', 146.20, 145.50, 1.50, 1050.00, -10.00, -3.50, 420, 'ACC001', 'Closed', 'JPY strength'),
('2024-02-05', 'GBP/USD', 'Buy', 1.26200, 1.26800, 1.80, 1080.00, -11.00, -4.00, 480, 'ACC001', 'Closed', 'Clean breakout'),
('2024-02-06', 'AUD/NZD', 'Sell', 1.08500, 1.08200, 1.20, 360.00, -8.50, -2.80, 300, 'ACC001', 'Closed', 'Cross pair success'),
('2024-02-07', 'EUR/GBP', 'Buy', 0.85200, 0.85600, 1.60, 640.00, -10.50, -3.50, 360, 'ACC001', 'Closed', 'Euro momentum'),
('2024-02-08', 'USD/CHF', 'Buy', 0.87200, 0.87000, 1.00, -200.00, -7.50, -2.00, 240, 'ACC001', 'Closed', 'Small loss'),
('2024-02-09', 'NZD/USD', 'Sell', 0.61800, 0.62100, 1.40, -420.00, -9.50, -3.00, 360, 'ACC001', 'Closed', 'Wrong direction'),
('2024-02-12', 'EUR/USD', 'Buy', 1.07500, 1.08000, 2.20, 1100.00, -13.00, -4.50, 540, 'ACC001', 'Closed', 'Big move'),
('2024-02-13', 'GBP/JPY', 'Buy', 187.20, 188.50, 1.50, 1950.00, -10.00, -4.00, 600, 'ACC001', 'Closed', 'Excellent trade'),
('2024-02-14', 'CAD/JPY', 'Sell', 109.80, 109.50, 1.00, 300.00, -7.50, -2.30, 240, 'ACC001', 'Closed', 'Valentine profit'),
('2024-02-15', 'EUR/JPY', 'Buy', 160.50, 161.20, 1.80, 1260.00, -11.00, -4.00, 420, 'ACC001', 'Closed', 'Strong follow-through'),
('2024-02-16', 'AUD/USD', 'Buy', 0.65200, 0.65600, 2.00, 800.00, -12.00, -4.00, 360, 'ACC001', 'Closed', 'Commodity rally'),
('2024-02-19', 'USD/CAD', 'Sell', 1.35500, 1.35800, 1.20, -360.00, -8.50, -2.80, 300, 'ACC001', 'Closed', 'Oil reversal'),
('2024-02-20', 'EUR/USD', 'Sell', 1.08500, 1.08200, 1.50, 450.00, -10.00, -3.20, 240, 'ACC001', 'Closed', 'Profit taking'),
('2024-02-21', 'GBP/USD', 'Buy', 1.26500, 1.27100, 2.50, 1500.00, -14.00, -5.00, 480, 'ACC001', 'Closed', 'Major win'),
('2024-02-22', 'NZD/JPY', 'Buy', 91.30, 91.80, 1.30, 650.00, -9.00, -3.00, 360, 'ACC001', 'Closed', 'Kiwi strength'),
('2024-02-23', 'EUR/GBP', 'Sell', 0.85900, 0.85600, 1.40, 420.00, -9.50, -3.20, 300, 'ACC001', 'Closed', 'Steady profit'),
('2024-02-26', 'USD/JPY', 'Buy', 147.50, 147.90, 1.60, 640.00, -10.50, -3.50, 360, 'ACC001', 'Closed', 'Good timing'),
('2024-02-27', 'AUD/CAD', 'Buy', 0.89200, 0.89600, 1.10, 440.00, -8.00, -2.80, 300, 'ACC001', 'Closed', 'Cross strength'),
('2024-02-28', 'EUR/USD', 'Buy', 1.08100, 1.08400, 1.80, 540.00, -11.00, -3.50, 420, 'ACC001', 'Closed', 'Month-end positive'),
('2024-03-01', 'GBP/USD', 'Sell', 1.27500, 1.27800, 1.20, -360.00, -8.50, -2.80, 300, 'ACC001', 'Closed', 'False signal'),
('2024-03-04', 'EUR/JPY', 'Buy', 161.80, 162.50, 1.50, 1050.00, -10.00, -3.50, 480, 'ACC001', 'Closed', 'Strong open'),
('2024-03-05', 'USD/CHF', 'Sell', 0.88500, 0.88200, 1.30, 390.00, -9.00, -3.00, 360, 'ACC001', 'Closed', 'CHF strength'),
('2024-03-06', 'NZD/USD', 'Buy', 0.61200, 0.61800, 2.00, 1200.00, -12.00, -4.00, 540, 'ACC001', 'Closed', 'Excellent move'),
('2024-03-07', 'EUR/USD', 'Buy', 1.09200, 1.09600, 1.40, 560.00, -9.50, -3.20, 360, 'ACC001', 'Closed', 'Trend play'),
('2024-03-08', 'GBP/JPY', 'Sell', 189.20, 189.60, 1.00, -400.00, -7.50, -2.50, 240, 'ACC001', 'Closed', 'Against trend'),
('2024-03-11', 'CAD/JPY', 'Buy', 110.50, 111.20, 1.60, 1120.00, -10.50, -3.80, 420, 'ACC001', 'Closed', 'CAD recovery'),
('2024-03-12', 'AUD/USD', 'Sell', 0.66200, 0.66500, 1.50, -450.00, -10.00, -3.20, 360, 'ACC001', 'Closed', 'Lost momentum'),
('2024-03-13', 'EUR/GBP', 'Buy', 0.85500, 0.85900, 1.80, 720.00, -11.00, -3.80, 480, 'ACC001', 'Closed', 'GBP weakness'),
('2024-03-14', 'USD/CAD', 'Buy', 1.36200, 1.36600, 1.20, 480.00, -8.50, -3.00, 300, 'ACC001', 'Closed', 'Oil dip'),
('2024-03-15', 'EUR/USD', 'Sell', 1.09800, 1.09500, 2.00, 600.00, -12.00, -4.00, 360, 'ACC001', 'Closed', 'Reversal trade'),
('2024-03-18', 'GBP/USD', 'Buy', 1.27200, 1.27800, 2.20, 1320.00, -13.00, -4.50, 540, 'ACC001', 'Closed', 'Strong rally'),
('2024-03-19', 'USD/JPY', 'Sell', 149.50, 149.00, 1.40, 700.00, -9.50, -3.20, 420, 'ACC001', 'Closed', 'JPY intervention fears'),
('2024-03-20', 'AUD/NZD', 'Buy', 1.08800, 1.09200, 1.00, 400.00, -7.50, -2.50, 300, 'ACC001', 'Closed', 'Aussie lead'),
('2024-03-21', 'EUR/JPY', 'Buy', 163.20, 164.10, 1.70, 1530.00, -10.80, -4.00, 480, 'ACC001', 'Closed', 'Big winner'),
('2024-03-22', 'NZD/USD', 'Sell', 0.61500, 0.61800, 1.30, -390.00, -9.00, -3.00, 360, 'ACC001', 'Closed', 'Early exit'),
('2024-03-25', 'EUR/USD', 'Buy', 1.08300, 1.08800, 2.50, 1250.00, -14.00, -5.00, 600, 'ACC001', 'Closed', 'Major move'),
('2024-03-26', 'GBP/JPY', 'Buy', 190.50, 191.20, 1.20, 840.00, -8.50, -3.20, 420, 'ACC001', 'Closed', 'Volatility win'),
('2024-03-27', 'USD/CHF', 'Buy', 0.89200, 0.89500, 1.50, 450.00, -10.00, -3.50, 300, 'ACC001', 'Closed', 'CHF weakness'),
('2024-03-28', 'CAD/JPY', 'Sell', 111.80, 111.50, 1.00, 300.00, -7.50, -2.30, 240, 'ACC001', 'Closed', 'Small profit'),
('2024-04-01', 'EUR/USD', 'Buy', 1.07800, 1.08500, 2.80, 1960.00, -15.00, -5.50, 540, 'ACC001', 'Closed', 'Quarter start strong'),
('2024-04-02', 'GBP/USD', 'Buy', 1.26800, 1.27500, 2.00, 1400.00, -12.00, -4.20, 480, 'ACC001', 'Closed', 'Momentum continue'),
('2024-04-03', 'USD/JPY', 'Sell', 150.20, 149.50, 1.60, 1120.00, -10.50, -3.80, 420, 'ACC001', 'Closed', 'Intervention worry'),
('2024-04-04', 'AUD/USD', 'Buy', 0.65800, 0.66400, 2.20, 1320.00, -13.00, -4.50, 540, 'ACC001', 'Closed', 'Commodity boom'),
('2024-04-05', 'EUR/GBP', 'Sell', 0.86200, 0.85900, 1.40, 420.00, -9.50, -3.20, 360, 'ACC001', 'Closed', 'Divergence'),
('2024-04-08', 'NZD/USD', 'Buy', 0.60800, 0.61500, 2.40, 1680.00, -14.00, -5.00, 600, 'ACC001', 'Closed', 'Huge gain'),
('2024-04-09', 'CAD/JPY', 'Buy', 112.20, 112.90, 1.50, 1050.00, -10.00, -3.60, 480, 'ACC001', 'Closed', 'Oil rally'),
('2024-04-10', 'EUR/USD', 'Sell', 1.08800, 1.08500, 1.80, 540.00, -11.00, -3.80, 360, 'ACC001', 'Closed', 'Profit lock'),
('2024-04-11', 'GBP/JPY', 'Buy', 192.30, 193.50, 1.40, 1680.00, -9.50, -3.80, 540, 'ACC001', 'Closed', 'Breakout trade'),
('2024-04-12', 'USD/CAD', 'Sell', 1.37500, 1.37200, 1.20, 360.00, -8.50, -2.80, 300, 'ACC001', 'Closed', 'Quick profit'),
('2024-04-15', 'EUR/JPY', 'Buy', 165.20, 166.40, 1.90, 2280.00, -11.50, -4.20, 600, 'ACC001', 'Closed', 'Monster trade'),
('2024-04-16', 'AUD/CAD', 'Buy', 0.90500, 0.91000, 1.30, 650.00, -9.00, -3.20, 420, 'ACC001', 'Closed', 'Cross win'),
('2024-04-17', 'EUR/USD', 'Buy', 1.06500, 1.07200, 2.60, 1820.00, -14.50, -5.00, 540, 'ACC001', 'Closed', 'Large position win'),
('2024-04-18', 'GBP/USD', 'Sell', 1.27800, 1.27500, 1.50, 450.00, -10.00, -3.30, 360, 'ACC001', 'Closed', 'Correction play'),
('2024-04-19', 'NZD/JPY', 'Buy', 92.50, 93.30, 1.60, 1280.00, -10.50, -3.80, 480, 'ACC001', 'Closed', 'Strong cross'),
('2024-04-22', 'USD/CHF', 'Buy', 0.90500, 0.91000, 1.40, 700.00, -9.50, -3.30, 420, 'ACC001', 'Closed', 'Safe haven shift'),
('2024-04-23', 'EUR/GBP', 'Buy', 0.86500, 0.86900, 1.70, 680.00, -10.80, -3.60, 360, 'ACC001', 'Closed', 'Euro strength'),
('2024-04-24', 'CAD/JPY', 'Sell', 113.50, 113.20, 1.10, 330.00, -8.00, -2.80, 300, 'ACC001', 'Closed', 'Small win'),
('2024-04-25', 'AUD/USD', 'Buy', 0.65200, 0.65900, 2.50, 1750.00, -14.00, -5.00, 600, 'ACC001', 'Closed', 'Big AUD move'),
('2024-04-26', 'EUR/USD', 'Buy', 1.07200, 1.07800, 2.20, 1320.00, -13.00, -4.50, 480, 'ACC001', 'Closed', 'Continuation'),
('2024-04-29', 'GBP/JPY', 'Buy', 194.20, 195.50, 1.50, 1950.00, -10.00, -4.00, 540, 'ACC001', 'Closed', 'Month-end surge'),
('2024-04-30', 'USD/JPY', 'Sell', 151.80, 151.20, 1.80, 1080.00, -11.00, -3.80, 420, 'ACC001', 'Closed', 'End strong');

-- Add a few more recent trades for variety
INSERT INTO forex_trades ("Trade_Date", "Symbol", "Trade_Type", "Entry_Price", "Exit_Price", "Lot_Size", "Daily_PnL", "Commission", "Swap", "Duration_Minutes", "Account_ID", "Status", "Notes")
VALUES
('2024-05-02', 'EUR/USD', 'Buy', 1.07500, 1.08100, 2.00, 1200.00, -12.00, -4.00, 480, 'ACC001', 'Closed', 'May start positive'),
('2024-05-03', 'GBP/USD', 'Sell', 1.27200, 1.26900, 1.60, 480.00, -10.50, -3.50, 360, 'ACC001', 'Closed', 'Short reversal'),
('2024-05-06', 'USD/JPY', 'Buy', 152.50, 153.20, 1.40, 980.00, -9.50, -3.20, 420, 'ACC001', 'Closed', 'JPY weakness'),
('2024-05-07', 'AUD/NZD', 'Sell', 1.09500, 1.09200, 1.20, 360.00, -8.50, -2.80, 300, 'ACC001', 'Closed', 'NZD strength'),
('2024-05-08', 'EUR/JPY', 'Buy', 167.30, 168.20, 1.80, 1620.00, -11.00, -4.00, 540, 'ACC001', 'Closed', 'Excellent setup'),
('2024-05-09', 'CAD/JPY', 'Buy', 114.50, 115.10, 1.30, 780.00, -9.00, -3.20, 360, 'ACC001', 'Closed', 'CAD momentum'),
('2024-05-10', 'NZD/USD', 'Sell', 0.61800, 0.61500, 1.50, 450.00, -10.00, -3.30, 420, 'ACC001', 'Closed', 'Weak data'),
('2024-05-13', 'EUR/USD', 'Buy', 1.08500, 1.09200, 2.40, 1680.00, -14.00, -4.80, 540, 'ACC001', 'Closed', 'Strong trend'),
('2024-05-14', 'GBP/JPY', 'Sell', 196.80, 196.20, 1.10, 660.00, -8.00, -2.90, 360, 'ACC001', 'Closed', 'Profit taking');

-- Display summary statistics
SELECT 
    COUNT(*) as total_trades,
    SUM("Daily_PnL") as total_pnl,
    AVG("Daily_PnL") as avg_pnl,
    MAX("Daily_PnL") as max_profit,
    MIN("Daily_PnL") as max_loss,
    COUNT(CASE WHEN "Daily_PnL" > 0 THEN 1 END) as profitable_trades,
    COUNT(CASE WHEN "Daily_PnL" < 0 THEN 1 END) as losing_trades,
    ROUND(COUNT(CASE WHEN "Daily_PnL" > 0 THEN 1 END) * 100.0 / COUNT(*), 2) as win_percentage
FROM forex_trades;

-- Display trades by symbol
SELECT 
    "Symbol",
    COUNT(*) as trade_count,
    SUM("Daily_PnL") as total_pnl,
    AVG("Daily_PnL") as avg_pnl
FROM forex_trades
GROUP BY "Symbol"
ORDER BY total_pnl DESC;

-- Display monthly performance
SELECT 
    DATE_TRUNC('month', "Trade_Date") as month,
    COUNT(*) as trades,
    SUM("Daily_PnL") as monthly_pnl,
    AVG("Daily_PnL") as avg_trade
FROM forex_trades
GROUP BY month
ORDER BY month;
