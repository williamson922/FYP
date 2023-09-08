import React, { useContext, useState, useEffect } from "react";
import ApexChart from "./ApexChart";
import DatePicker from "react-datepicker"; // Import a date picker library
import "react-datepicker/dist/react-datepicker.css"; // Import date picker styles
import { DataContext } from "./DataProvider";
import "../../css/dashboard.css";

const Dashboard = () => {
    const {
        predictedData,
        date,
        setDate,
        historicalActualDataADay,
        historicalPredictedDataADay,
        historicalActualDataTwoDays,
        historicalPredictedDataTwoDays,
        mapeThreshold,
    } = useContext(DataContext);
    const [totalEnergyYesterday, setTotalEnergyYesterday] = useState(0);
    const [totalEnergyPastTwoDays, setTotalEnergyPastTwoDays] = useState(0);
    const [totalCostYesterday, setTotalCostYesterday] = useState(0);
    const [totalCostPastTwoDays, setTotalCostPastTwoDays] = useState(0);
    const [mapePastTwoDays, setMapePastTwoDays] = useState(0);
    const [mapeYesterday, setMapeYesterday] = useState(0);
    const [selectedDate, setSelectedDate] = useState(new Date());

    const yesterday = new Date(date);
    yesterday.setDate(date.getDate() - 1);
    const pastTwoDays = new Date(date);
    pastTwoDays.setDate(date.getDate() - 2);

    // Calculate peak power consumption
    const peakPowerEntry =
        historicalActualDataADay.length > 0
            ? historicalActualDataADay.reduce((maxEntry, entry) => {
                  if (entry["Total Power"] > maxEntry["Total Power"]) {
                      return entry;
                  }
                  return maxEntry;
              }, historicalActualDataADay[0])
            : null;

    const lowestPowerEntry =
        historicalActualDataADay.length > 0
            ? historicalActualDataADay.reduce((minEntry, entry) => {
                  if (entry["Total Power"] < minEntry["Total Power"]) {
                      return entry;
                  }
                  return entry;
              })
            : null;

    function calculateTotalEnergy(actualData) {
        if (actualData.length > 0) {
            let total = 0;
            for (let entry of actualData) {
                if ("Total Power" in entry) {
                    total += entry["Total Power"];
                } else if ("predicted power" in entry) {
                    total += entry["predicted power"];
                }
            }
            return (total / 1000).toFixed(2);
        } else {
            return 0; // Set to zero when no data available
        }
    }

    function calculateCost(totalEnergy) {
        let cost = totalEnergy * 0.365;
        return cost.toFixed(2);
    }

    useEffect(() => {
        setMapeYesterday(
            calculateMAPE(historicalActualDataADay, historicalPredictedDataADay)
        );
        setTotalEnergyYesterday(calculateTotalEnergy(historicalActualDataADay));

        setMapePastTwoDays(
            calculateMAPE(
                historicalActualDataTwoDays,
                historicalPredictedDataTwoDays
            )
        );
        setTotalEnergyPastTwoDays(
            calculateTotalEnergy(historicalActualDataTwoDays)
        );
    }, [historicalActualDataADay, historicalActualDataTwoDays, date]);
    useEffect(() => {
        setTotalCostYesterday(calculateCost(totalEnergyYesterday));
        setTotalCostPastTwoDays(calculateCost(totalEnergyPastTwoDays));
    }, [totalEnergyYesterday, totalEnergyPastTwoDays]);

    function calculateMAPE(actualData, predictedData) {
        if (actualData.length > 0 && predictedData.length > 0) {
            if (actualData.length !== predictedData.length) {
                throw new Error(
                    "Actual and predicted data arrays must have the same length."
                );
            }

            const n = actualData.length;

            // Calculate the sum of absolute percentage errors
            let sumAPE = 0;
            for (let i = 0; i < n; i++) {
                const actual = actualData[i]["Total Power"];
                const predicted = predictedData[i]["predicted power"];
                if (actual === 0) {
                    // Handle division by zero, consider it as a perfect prediction
                    sumAPE += 0;
                } else {
                    const ape = Math.abs((actual - predicted) / actual) * 100;
                    sumAPE += ape;
                }
            }

            // Calculate the mean APE
            const meanAPE = sumAPE / n;

            return meanAPE.toFixed(2);
        } else {
            return 0;
        }
    }

    function evaluatePerformance(mape) {
        // Define your criteria here, for example, a threshold of 10%
        const threshold = mapeThreshold;

        if (mape <= threshold) {
            return "✅"; // Good performance, return a tick
        } else {
            return "❌"; // Bad performance, return a cross
        }
    }

    const peakPower = peakPowerEntry ? peakPowerEntry["Total Power"] : 0;
    const lowestPower = lowestPowerEntry ? lowestPowerEntry["Total Power"] : 0;
    // Find peak and lowest usage times
    const peakUsageEntry =
        Array.isArray(historicalActualDataADay) &&
        historicalActualDataADay.length > 0
            ? historicalActualDataADay.reduce((maxEntry, entry) => {
                  if (entry["Total Power"] > maxEntry["Total Power"]) {
                      return entry;
                  }
                  return maxEntry;
              }, historicalActualDataADay[0])
            : null;

    const lowestUsageEntry =
        Array.isArray(historicalActualDataADay) &&
        historicalActualDataADay.length > 0
            ? historicalActualDataADay.reduce((minEntry, entry) => {
                  if (entry["Total Power"] < minEntry["Total Power"]) {
                      return entry;
                  }
                  return minEntry;
              }, historicalActualDataADay[0])
            : null;

    const peakUsageTime = peakUsageEntry
        ? new Date(peakUsageEntry["Date/Time"]).toLocaleTimeString()
        : "No Peak Time ";
    const lowestUsageTime = lowestUsageEntry
        ? new Date(lowestUsageEntry["Date/Time"]).toLocaleTimeString()
        : "No Lowest Time";

    return (
        <div className="dashboard">
            <main className="dashboard-content">
                {/* Date Picker */}
                <div className="date-picker">
                    <label>Select Date: </label>
                    <DatePicker
                        selected={date}
                        onChange={(date) => setDate(date)}
                        dateFormat="yyyy-MM-dd"
                        maxDate={new Date()} // Optional: restrict selection to past dates
                    />
                </div>
                <div className="data-sections">
                    {/* Historical Graph */}
                    <div className="dashboard-section">
                        <h2>Historical Graph</h2>
                        {historicalActualDataADay.length > 0 ||
                        historicalPredictedDataADay.length > 0 ? (
                            <ApexChart
                                dataType="historical total power"
                                label="Power(kW)"
                            />
                        ) : (
                            <p>
                                <strong>No data available.</strong>
                            </p>
                        )}
                        {historicalActualDataADay.length > 0 && (
                            <div className="data-row">
                                <p className="data-label">
                                    Historical Actual Data Total Energy Usage:{" "}
                                </p>
                                <p className="data-value">
                                    {calculateTotalEnergy(
                                        historicalActualDataADay
                                    )}{" "}
                                    kW
                                </p>
                            </div>
                        )}
                        {historicalPredictedDataADay.length > 0 && (
                            <div className="data-row">
                                <p className="data-label">
                                    Historical Predicted Data Total Energy
                                    Usage:{" "}
                                </p>
                                <p className="data-value">
                                    {calculateTotalEnergy(
                                        historicalPredictedDataADay
                                    )}{" "}
                                    kW
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Predicted Graph */}
                    <div className="dashboard-section">
                        <h2>Predicted Graph</h2>
                        {predictedData.length > 0 ? (
                            <ApexChart
                                dataType="total power"
                                label="Power(kW)"
                            />
                        ) : (
                            <p>
                                <strong>No data available.</strong>
                            </p>
                        )}
                        {predictedData.length > 0 && (
                            <div className="data-row">
                                <p className="data-label">
                                    Predicted Data Total Energy Usage:{" "}
                                </p>
                                <p className="data-value">
                                    {calculateTotalEnergy(predictedData)} kW
                                </p>
                            </div>
                        )}
                    </div>
                    <div className="tables-row">
                        {/* Analysis Table */}
                        <div className="dashboard-section">
                            <h2>Analysis Table</h2>
                            <table className="axis-1-table">
                                <tbody>
                                    {Object.entries({
                                        "Peak Usage Time": peakUsageTime,
                                        "Peak Load": `${(peakPower/1000).toFixed(2)} kW`,
                                        "Lowest Usage Time": lowestUsageTime,
                                        "Lowest Load": `${(lowestPower/1000).toFixed(2)} kW`,
                                    }).map(([key, value]) => (
                                        <tr key={key}>
                                            <th>{key}</th>
                                            <td>{value}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        {/* Historical Table */}
                        <div className="dashboard-section">
                            <h2>Historical Table</h2>
                            <table className="axis-0-table">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>MAPE</th>
                                        <th>Remarks</th>
                                        <th>kWh</th>
                                        <th>Cost</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>
                                            {yesterday.toLocaleDateString()}
                                        </td>
                                        <td>{mapeYesterday}%</td>
                                        <td>
                                            {evaluatePerformance(mapeYesterday)}
                                        </td>
                                        <td>{totalEnergyYesterday} kWh</td>
                                        <td>RM {totalCostYesterday}</td>
                                    </tr>
                                    <tr>
                                        <td>
                                            {pastTwoDays.toLocaleDateString()}
                                        </td>
                                        <td>{mapePastTwoDays}%</td>
                                        <td>
                                            {evaluatePerformance(
                                                mapePastTwoDays
                                            )}
                                        </td>
                                        <td>{totalEnergyPastTwoDays} kWh</td>
                                        <td>RM {totalCostPastTwoDays}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};
export default Dashboard;
