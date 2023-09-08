import React, { useContext, useState, useEffect } from 'react';
import ApexChart from './ApexChart';
import {DataContext} from './DataProvider';

const AnalyticsChart=()=>{
    const {actualData} = useContext(DataContext)
    const properties = actualData.length > 0 ? Object.keys(actualData[0]) : [];
    return (
        <div className="analytics-chart">
          <h2>Energy Analytics</h2>
          <div className="charts">
            <h3>Voltage Phase A</h3>
            <ApexChart dataType="Voltage Ph-A Avg" label="Voltage(V)" />
            <h3>Voltage Phase B</h3>
            <ApexChart dataType="Voltage Ph-B Avg" label="Voltage(V)" />
            <h3>Voltage Phase C</h3>
            <ApexChart dataType="Voltage Ph-C Avg" label="Voltage(V)" />
            <h3>Current Phase A</h3>
            <ApexChart dataType="Current Ph-A Avg" label="Current(A)" />
            <h3>Current Phase B</h3>
            <ApexChart dataType="Current Ph-B Avg" label="Current(A)" />
            <h3>Current Phase C</h3>
            <ApexChart dataType="Current Ph-C Avg" label="Current(A)" />
            <h3>Power Phase A</h3>
            <ApexChart dataType="Power Ph-A" label="Power(W)" />
            <h3>Power Phase B</h3>
            <ApexChart dataType="Power Ph-B" label="Power(W)" />
            <h3>Power Phase C</h3>
            <ApexChart dataType="Power Ph-C" label="Power(W)" />
          </div>
        </div>
      );
    };

export default AnalyticsChart;
