import React, {useState,useContext}from "react";
import ReactApexChart from 'react-apexcharts';
import {DataContext} from './DataProvider';

// const ApexChart = (energyData,predictedData) => {
  const ApexChart = () => {

  const {predictedData,actualData} = useContext(DataContext);
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
      enabled: false,
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
      // categories: ['00:00', '03:00','06:00', '09:00','12:00', '15:00','18:00', '21:00','23:59'],
      title: {
        text: 'Time'
      },
      type: 'category',
      categories: [
      '00:00', '00:30', '01:00', '01:30', '02:00', '02:30',
      '03:00', '03:30', '04:00', '04:30', '05:00', '05:30',
      '06:00', '06:30', '07:00', '07:30', '08:00', '08:30',
      '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
      '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
      '15:00', '15:30', '16:00', '16:30', '17:00', '17:30',
      '18:00', '18:30', '19:00', '19:30', '20:00', '20:30',
      '21:00', '21:30', '22:00', '22:30', '23:00', '23:30',
    ],
    },
    yaxis: {
      title: {
        text: 'Power(kW)'
      },
      min: 0,
      max: 20,
      labels: {
        formatter: function (value) {
          // Check if the value is not undefined before formatting
          if (value !== undefined) {
            // Format the label to have two decimal places
            return value.toFixed(2);
          }
          return ""; // Return an empty string if the value is undefined
        },
      },
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
  //   {
  //     name: 'Actual',
  //     data: [28, 29, 33, 36, 32, 32, 33]
  //   },
  //   {
  //     name: 'Predicted',
  //     data: [12, 11, 14, 18, 17, 13, 13, 36, 32, 32, 33]
  //   }
  // ]);
  {
    name: 'Actual',
    data: actualData.map(entry => (entry['Total Power']/1000).toFixed(2))
  },
  {
    name: 'Predicted',
    data: predictedData.map(entry => (entry['Predicted Load']/1000).toFixed(2))
  }
]);

  return (
    <div id="chart">
      <ReactApexChart options={chartOptions} series={chartSeries} type="line" height={350} />
    </div>
  );
};

export default ApexChart;