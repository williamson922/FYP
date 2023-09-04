import React, {useState,useContext}from "react";
import ReactApexChart from 'react-apexcharts';
import {DataContext} from './DataProvider';

// const ApexChart = (energyData,predictedData) => {
  const ApexChart = ({dataType,label}) => {

  const {predictedData,actualData} = useContext(DataContext);
  // Format the x-axis labels to show only the hour
  const xAxisLabelsFormatted = predictedData.map(entry => {
    const dateTime = entry["Date/Time"];
    if (dateTime) {
      return new Date(dateTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }
    return "";
  });

  let chartTitle = actualData.length > 0 ? new Date(actualData[0]["Date/Time"]).toLocaleDateString("en-GB", {
    year: "numeric",
    month: "numeric",
    day: "numeric",
  }) : "";
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
        show: true,
        tools:{
          download:false,
        },
        autoSelected:"zoom",
      },
    },
    colors: ['#77B6EA', '#545454'],
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: 'smooth'
    },
    title: {
      text: chartTitle,
      align: 'center'
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
      title:{
        text:"Time"
      },
      type: "category",
      categories: xAxisLabelsFormatted,
      labels: {
        formatter: function (value) {
          return value; // Simply return the formatted time label
        },
      },
    },
    yaxis: {
      title: {
        text: label
      },
      min: 0,
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
  let chartSeries = [];
  if(dataType == "total power"){
     chartSeries = [
      {
        name: "Actual",
        data: actualData.map(entry => (entry["Total Power"] / 1000).toFixed(2)),
      },
      {
        name: "Predicted",
        data: predictedData.map(entry => (entry["predicted power"] / 1000).toFixed(2)),
      },
    ];
  }
  else {
     chartSeries = [

      {
        name: dataType,
        data: actualData.map(entry => entry[dataType]),
      },
    ];
  }

    // Find the maximum value in the chartSeries data
    const maxValue = Math.max(...chartSeries.flatMap(serie => serie.data.map(Number)));

    // Round up the maximum value to the nearest integer
    const roundedMaxValue = Math.ceil(maxValue);
  
    // Update the y-axis maximum value with the rounded integer
    chartOptions.yaxis.max = roundedMaxValue;


  return (
    <div id="chart">
      <ReactApexChart options={chartOptions} series={chartSeries} type="line" height={350} />
    </div>
  );
};

export default ApexChart;