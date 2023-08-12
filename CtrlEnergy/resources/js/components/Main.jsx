import React, { useState, useEffect } from 'react';
import {createRoot} from 'react-dom/client';
import axios from 'axios';
import {DataContext,DataProvider} from './DataProvider'
import HolidayForm from './HolidayForm';
import Dashboard from './Dashboard';
import FileUpload from './FileUpload';
import '../../css/main.css'

const Main = () => {

  const [fileData, setFileData] = useState(null);

  const handleDateChange = (e) => {
    setSelectedDate(e.target.value);
  };

  const filterDataByDate = () => {
    const filteredData = energyData.filter((entry) => entry.date === selectedDate);
    calculateTotalEnergy(filteredData);
  };

  const [selectedNavItem, setSelectedNavItem] = useState('dashboard');

  const handleNavItemSelect = (item) => {
    setSelectedNavItem(item);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Welcome to the Dashboard!</h1>
      </header>
      <main className="dashboard-content">
        <div className="dashboard-sidebar">
          <nav>
            <ul>
              <li
                className={selectedNavItem === 'dashboard' ? 'active' : ''}
                onClick={() => handleNavItemSelect('dashboard')}
              >
                <i className="fas fa-home"></i> Dashboard
              </li>
              <li
                className={selectedNavItem === 'analytics' ? 'active' : ''}
                onClick={() => handleNavItemSelect('analytics')}
              >
                <i className="fas fa-chart-line"></i> Analytics
              </li>
              <li
                className={selectedNavItem === 'holiday' ? 'active' : ''}
                onClick={() => handleNavItemSelect('holiday')}
              >
                <i className="fas fa-cog"></i> Holiday Form
              </li>
              <li
                className={selectedNavItem === 'fileUpload' ? 'active' : ''}
                onClick={() => handleNavItemSelect('fileUpload')}
              >
                <i className="fas fa-cog"></i> Upload File
              </li>
              <li
                className={selectedNavItem === 'settings' ? 'active' : ''}
                onClick={() => handleNavItemSelect('settings')}
              >
                <i className="fas fa-cog"></i> Settings
              </li>
            </ul>
          </nav>
        </div>
        <div className="dashboard-main">
          {selectedNavItem === 'dashboard' && (
            <div>
              {/* Render dashboard content */}
              <Dashboard />
            </div>
          )}
          {selectedNavItem === 'analytics' && (
            <div>
              {/* Render analytics content */}
              <h2>Analytics Content</h2>
            </div>
          )}
          {selectedNavItem === 'holiday' && (
            <div>
              {/* Render holiday form */}
              <HolidayForm />
            </div>
          )}
          {selectedNavItem === 'fileUpload' && (
            <div>
              {/* Render holiday form */}
              <FileUpload />
            </div>
          )}
          {selectedNavItem === 'settings' && (
            <div>
              {/* Render settings content */}
              <h2>Settings Content</h2>
            </div>
          )}
        </div>
      </main>
      <footer className="dashboard-footer">
        <p>&copy; 2023 Your Company. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Main;

if (typeof document !== 'undefined') {
  createRoot(document.getElementById('main-page')).render(
  <DataProvider>
    <Main />
  </DataProvider>
  );
}
