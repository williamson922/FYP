import React, { useContext } from 'react';
import ApexChart from './ApexChart';
import {DataContext} from './DataProvider';

const Dashboard = () => {

  const {energyData, predictedData, totalEnergy} = useContext(DataContext);

   return (
    <div className="dashboard">
      <main className="dashboard-content">
        <div className="dashboard-section">
          <h2>Energy Consumption Comparison</h2>
          {energyData.length > 0 || predictedData.length > 0 ? (
            <ApexChart energyData={energyData} predictedData={predictedData} />
          ) : (
            <p><strong>No data available.</strong></p>
          )}
        </div>
        <div className="dashboard-section">
          <h2>Total Energy Consumption</h2>
          <p>{totalEnergy} kWh</p>
        </div>
        <div className="dashboard-section">
          <h2>Other Data Section</h2>
          {/* Display other data sections */}
        </div>
      </main>
    </div>
  );
};


export default Dashboard;


