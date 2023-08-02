import React, {useState,useContext}from "react";

import ReactApexChart from 'react-apexcharts';
import {DataContext} from './DataProvider';

// const ApexChart = (energyData,predictedData) => {
  const ApexChart = () => {
  const [chartOptions, setChartOptions] = useState({
    chart: {
      height: 350,
      type: 'line',
      dropShadow: {
        enabled: true,
        color: '#000',
        top: 18,
        left: 7,
        blur: 10,
        opacity: 0.2
      },
      toolbar: {
        show: false
      }
    },
    colors: ['#77B6EA', '#545454'],
    dataLabels: {
      enabled: true,
    },
    stroke: {
      curve: 'smooth'
    },
    title: {
      text: 'Energy Usage',
      align: 'left'
    },
    grid: {
      borderColor: '#e7e7e7',
      row: {
        colors: ['#f3f3f3', 'transparent'],
        opacity: 0.5
      },
    },
    markers: {
      size: 1
    },
    xaxis: {
      categories: ['00:00', '03:00','06:00', '09:00','12:00', '15:00','18:00', '21:00','23:59'],
      title: {
        text: 'Time'
      },
      min: '00:00',
      max: '23:59'
    },
    yaxis: {
      title: {
        text: 'Power(kW)'
      },
      min: 5,
      max: 40
    },
    legend: {
      position: 'top',
      horizontalAlign: 'right',
      floating: true,
      offsetY: -25,
      offsetX: -5
    }
  });

  const [chartSeries, setChartSeries] = useState([
    {
      name: 'Actual',
      data: [28, 29, 33, 36, 32, 32, 33]
    },
    {
      name: 'Predicted',
      data: [12, 11, 14, 18, 17, 13, 13, 36, 32, 32, 33]
    }
  ]);
//   {
//     name: 'Actual',
//     data: energyData.map(entry => entry.energy)
//   },
//   {
//     name: 'Predicted',
//     data: predictedData.map(entry => entry.energy)
//   }
// ]);

  return (
    <div id="chart">
      <ReactApexChart options={chartOptions} series={chartSeries} type="line" height={350} />
    </div>
  );
};

export default ApexChart;