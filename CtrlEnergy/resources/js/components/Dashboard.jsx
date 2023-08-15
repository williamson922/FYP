import React, { useContext, useState, useEffect } from 'react';
import ApexChart from './ApexChart';
import {DataContext} from './DataProvider';
import '../../css/dashboard.css';

const Dashboard = () => {
  const { actualData, predictedData} = useContext(DataContext);
  const {totalEnergy,setTotalEnergy} = useState(0)
  // Calculate peak power consumption
  const peakPowerEntry = actualData.length > 0 ? actualData.reduce((maxEntry, entry) => {
    if (entry['Total Power'] > maxEntry['Total Power']) {
      return entry;
    }
    return maxEntry;
  }, actualData[0]) : null;

  const calculateTotalEnergy = () => {
    if (actualData.length > 0) {
      let total = 0;
      for (let entry of actualData) {
        total += entry['Total Power'];
      }
      setTotalEnergy((total / 1000).toFixed(2));
    }
  };
    // Calculate total energy whenever actualData changes
    useEffect(() => {
      calculateTotalEnergy();
    }, []);

  const peakPower = peakPowerEntry ? peakPowerEntry['Total Power'] : 0;

  // Calculate energy efficiency
  const actualTotalPower = Array.isArray(actualData)
    ? actualData.reduce((total, entry) => total + entry['Total Power'], 0)
    : 0;

  const predictedTotalPower = Array.isArray(predictedData)
    ? predictedData.reduce((total, entry) => total + entry['predicted power'], 0)
    : 0;

  const energyEfficiency = predictedTotalPower !== 0 ? ((actualTotalPower / predictedTotalPower) * 100).toFixed(2) : 0;

  // Find peak and lowest usage times
  const peakUsageEntry = Array.isArray(actualData) && actualData.length > 0
    ? actualData.reduce((maxEntry, entry) => {
      if (entry['Total Power'] > maxEntry['Total Power']) {
        return entry;
      }
      return maxEntry;
    }, actualData[0])
    : null;

  const lowestUsageEntry = Array.isArray(actualData) && actualData.length > 0
    ? actualData.reduce((minEntry, entry) => {
      if (entry['Total Power'] < minEntry['Total Power']) {
        return entry;
      }
      return minEntry;
    }, actualData[0])
    : null;

  const peakUsageTime = peakUsageEntry ? new Date(peakUsageEntry['Date/Time']).toLocaleTimeString() : 'No Peak Time ';
  const lowestUsageTime = lowestUsageEntry ? new Date(lowestUsageEntry['Date/Time']).toLocaleTimeString() : 'No Lowest Time';

  console.log('peakPower:', peakPower);
  console.log('actualTotalPower:', actualTotalPower);
  console.log('predictedTotalPower:', predictedTotalPower);
  console.log('peakUsageTime:', peakUsageTime);
  return (
    <div className="dashboard">
      <main className="dashboard-content">
        <div className="chart-section">
          <h2>Energy Consumption Comparison</h2>
          {actualData.length > 0 || predictedData.length > 0 ? (
            <ApexChart actualData={actualData} predictedData={predictedData} />
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


