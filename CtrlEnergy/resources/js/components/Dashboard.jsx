import React, { useContext } from 'react';
import ApexChart from './ApexChart';
import {DataContext} from './DataProvider';
import '../../css/dashboard.css';

const Dashboard = () => {
  const { energyData, predictedData, totalEnergy } = useContext(DataContext);

  // Calculate peak power consumption
  const peakPowerEntry = energyData.length > 0 ? energyData.reduce((maxEntry, entry) => {
    if (entry['Total Power'] > maxEntry['Total Power']) {
      return entry;
    }
    return maxEntry;
  }, energyData[0]) : null;

  const peakPower = peakPowerEntry ? peakPowerEntry['Total Power'] : 0;

  // Calculate energy efficiency
  const actualTotalPower = energyData.reduce((total, entry) => total + entry['Total Power'], 0);
  const predictedTotalPower = predictedData.reduce((total, entry) => total + entry['Predicted Load'], 0);
  const energyEfficiency = predictedTotalPower !== 0 ? ((actualTotalPower / predictedTotalPower) * 100).toFixed(2) : 0;

  // Find peak and lowest usage times
  const peakUsageEntry = energyData.length > 0 ? energyData.reduce((maxEntry, entry) => {
    if (entry['Total Power'] > maxEntry['Total Power']) {
      return entry;
    }
    return maxEntry;
  }, energyData[0]) : null;

  const lowestUsageEntry = energyData.length > 0 ? energyData.reduce((minEntry, entry) => {
    if (entry['Total Power'] < minEntry['Total Power']) {
      return entry;
    }
    return minEntry;
  }, energyData[0]) : null;

  const peakUsageTime = peakUsageEntry ? peakUsageEntry['Date/Time'].toLocaleTimeString() : 'No Peak Time ';
  const lowestUsageTime = lowestUsageEntry ? lowestUsageEntry['Date/Time'].toLocaleTimeString() : 'No Lowest Time';

  return (
    <div className="dashboard">
      <main className="dashboard-content">
        <div className="chart-section">
          <h2>Energy Consumption Comparison</h2>
          {energyData.length > 0 || predictedData.length > 0 ? (
            <ApexChart energyData={energyData} predictedData={predictedData} />
          ) : (
            <p><strong>No data available.</strong></p>
          )}
        </div>
        <div className="data-sections">
          <div className="dashboard-section">
            <h2>Total Energy Consumption</h2>
            <p>{totalEnergy} kWh</p>
          </div>
          <div className="dashboard-section">
            <h2>Peak Power Consumption</h2>
            <p>{peakPower.toFixed(2)} kW</p>
          </div>
          <div className="dashboard-section">
            <h2>Energy Efficiency</h2>
            <p>{energyEfficiency}%</p>
          </div>
          <div className="dashboard-section">
            <h2>Peak Usage Time</h2>
            <p>{peakUsageTime}</p>
          </div>
          <div className="dashboard-section">
            <h2>Lowest Usage Time</h2>
            <p>{lowestUsageTime}</p>
          </div>
        </div>
      </main>
    </div>
  );
  
            }
export default Dashboard;


