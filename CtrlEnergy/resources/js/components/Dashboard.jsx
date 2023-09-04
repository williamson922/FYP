import React, { useContext, useState, useEffect } from 'react';
import ApexChart from './ApexChart';
import DatePicker from 'react-datepicker'; // Import a date picker library
import 'react-datepicker/dist/react-datepicker.css'; // Import date picker styles
import {DataContext} from './DataProvider';
import '../../css/dashboard.css';

const Dashboard = () => {
  const { actualData, predictedData,date,setDate} = useContext(DataContext);
  const [totalEnergy,setTotalEnergy] = useState(0)
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [mape, setMape] = useState(0); // State variable for MAPE

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
    } else {
      setTotalEnergy(0); // Set to zero when no data available
    }
  };
    // Calculate total energy whenever actualData changes
    useEffect(() => {
      calculateTotalEnergy();
    }, [actualData]);

// Calculate MAPE
useEffect(() => {
  if (actualData.length > 0 && predictedData.length > 0) {
    const commonLength = Math.min(actualData.length, predictedData.length);

    const sumAPE = actualData.slice(0, commonLength).reduce((sum, actualEntry, index) => {
      const predictedEntry = predictedData[index];
      const absolutePercentageError = Math.abs(
        (actualEntry['Total Power'] - predictedEntry['predicted power']) /
        actualEntry['Total Power']
      );
      return sum + absolutePercentageError;
    }, 0);

    const meanAPE = sumAPE / commonLength;
    const mapeValue = meanAPE * 100;
    setMape(mapeValue);
  }
}, [actualData, predictedData]);
    
  const peakPower = peakPowerEntry ? peakPowerEntry['Total Power'] : 0;

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
  console.log('peakUsageTime:', peakUsageTime);
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
        <div className="chart-section">
          <h2>Energy Consumption Comparison</h2>
          {actualData.length > 0 || predictedData.length > 0 ? (
            <ApexChart dataType="total power" label="Power(kW)"/>
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
            <h2>Peak Usage Time</h2>
            <p>{peakUsageTime}</p>
          </div>
          <div className="dashboard-section">
            <h2>Lowest Usage Time</h2>
            <p>{lowestUsageTime}</p>
          </div>
          {/* Display the MAPE */}
          <div className="dashboard-section">
            <h2>Mean Absolute Percentage Error(MAPE)</h2>
            <p>{mape.toFixed(2)}%</p>
          </div>
        </div>
      </main>
    </div>
  );
  
            }
export default Dashboard;


