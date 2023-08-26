import React, { useContext, useState, useEffect } from 'react';
import ApexChart from './ApexChart';
import {DataContext} from './DataProvider';

const AnalyticsChart=()=>{
    const {actualData} = useContext(DataContext)
    const properties = actualData.length > 0 ? Object.keys(actualData[0]) : [];
    console.log("In AnalyticsChart,", properties)
    return (
        <div className="analytics-chart">
          <h2>Energy Analytics</h2>
          <div className="charts">
            <ApexChart dataType="Voltage Ph-A Avg" label="Voltage(V)" />
            <ApexChart dataType="Voltage Ph-B Avg" label="Voltage(V)" />
            <ApexChart dataType="Voltage Ph-C Avg" label="Voltage(V)" />
            <ApexChart dataType="Current Ph-A Avg" label="Current(A)" />
            <ApexChart dataType="Current Ph-B Avg" label="Current(A)" />
            <ApexChart dataType="Current Ph-C Avg" label="Current(A)" />
            <ApexChart dataType="Power Ph-A" label="Power(kW)" />
            <ApexChart dataType="Power Ph-B" label="Power(kW)" />
            <ApexChart dataType="Power Ph-C" label="Power(kW)" />
          </div>
        </div>
      );
    };

export default AnalyticsChart;
