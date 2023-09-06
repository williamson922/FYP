import React, { useState, useContext, useEffect } from "react";
import ReactApexChart from "react-apexcharts";
import { DataContext } from "./DataProvider";

// const ApexChart = (energyData,predictedData) => {
const ApexChart = ({ dataType, label }) => {
    const {
        predictedData,
        actualData,
        historicalActualDataADay,
        historicalPredictedDataADay,
        date,
    } = useContext(DataContext);
    // Initialize chartTitle and chartSeries as state variables
    const [chartTitle, setChartTitle] = useState("");
    const [chartSeries, setChartSeries] = useState([]);
    // Format the x-axis labels to show only the hour
    const xAxisLabelsFormatted = predictedData.map((entry) => {
        const dateTime = entry["Date/Time"];
        if (dateTime) {
            return new Date(dateTime).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
            });
        }
        return "";
    });

    const [chartOptions, setChartOptions] = useState({
        chart: {
            height: 350,
            type: "line",
            dropShadow: {
                enabled: true,
                color: "#000",
                top: 18,
                left: 7,
                blur: 10,
                opacity: 0.2,
            },
            toolbar: {
                show: true,
                tools: {
                    download: false,
                },
                autoSelected: "zoom",
            },
        },
        colors: ["#77B6EA", "#545454"],
        dataLabels: {
            enabled: false,
        },
        stroke: {
            curve: "smooth",
        },
        grid: {
            borderColor: "#e7e7e7",
            row: {
                colors: ["#f3f3f3", "transparent"],
                opacity: 0.5,
            },
        },
        markers: {
            size: 1,
        },
        xaxis: {
            title: {
                text: "Time",
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
                text: label,
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
            position: "top",
            horizontalAlign: "right",
            floating: true,
            offsetY: -25,
            offsetX: -5,
        },
    });

    useEffect(() => {
        // Function to update chart options
        const updateChartOptions = (newTitle) => {
            const updatedOptions = {
                ...chartOptions,
                title: { text: newTitle, align: "center" },
            };
            setChartTitle(newTitle);
            setChartOptions(updatedOptions);
  
        };

        // Define a function to update the chart series
        const updateChartSeries = (newData) => {
            setChartSeries(newData);
        };

        let updatedChartSeries = [];
        let updatedChartTitle = "";

        if (dataType == "historical total power") {
            updatedChartTitle =
                historicalActualDataADay.length > 0
                    ? new Date(
                          historicalActualDataADay[0]["Date/Time"]
                      ).toLocaleDateString("en-GB", {
                          year: "numeric",
                          month: "numeric",
                          day: "numeric",
                      })
                    : "";

            updateChartOptions(updatedChartTitle);
            updatedChartSeries = [
                {
                    name: "Actual",
                    data: historicalActualDataADay.map((entry) =>
                        (entry["Total Power"] / 1000).toFixed(2)
                    ),
                },
                {
                    name: "Predicted",
                    data: historicalPredictedDataADay.map((entry) =>
                        (entry["predicted power"] / 1000).toFixed(2)
                    ),
                },
            ];
            // Use the new method to update the chart series
            updateChartSeries(updatedChartSeries);
        } else if (dataType == "total power") {
            updatedChartTitle =
                predictedData.length > 0
                    ? new Date(
                          predictedData[0]["Date/Time"]
                      ).toLocaleDateString("en-GB", {
                          year: "numeric",
                          month: "numeric",
                          day: "numeric",
                      })
                    : "";
            updateChartOptions(updatedChartTitle);
            updatedChartSeries = [
                //  {
                //    name: "Actual",
                //    data: actualData.map(entry => (entry["Total Power"] / 1000).toFixed(2)),
                //  },
                {
                    name: "Predicted",
                    data: predictedData.map((entry) =>
                        (entry["predicted power"] / 1000).toFixed(2)
                    ),
                },
            ];
            // Use the new method to update the chart series
            updateChartSeries(updatedChartSeries);
        } else {
            updatedChartTitle =
                historicalActualDataADay.length > 0
                    ? new Date(
                          historicalActualDataADay[0]["Date/Time"]
                      ).toLocaleDateString("en-GB", {
                          year: "numeric",
                          month: "numeric",
                          day: "numeric",
                      })
                    : "";
            updateChartOptions(updatedChartTitle);
            updatedChartSeries = [
                {
                    name: dataType,
                    data: historicalActualDataADay.map((entry) => entry[dataType]),
                },
            ];
            // Use the new method to update the chart series
            updateChartSeries(updatedChartSeries);
        }
        // Find the maximum value in the updated chartSeries data
        const maxValue = Math.max(
            ...updatedChartSeries.flatMap((serie) => serie.data.map(Number))
        );

        // Round up the maximum value to the nearest integer
        const roundedMaxValue = Math.ceil(maxValue);

        // Update the y-axis maximum value with the rounded integer
        const updatedOptions = {
            ...chartOptions,
            title:{text:chartTitle,align:"center"},
            yaxis: {
              title: { text: label },
              max: roundedMaxValue,
          },
        };
        setChartOptions(updatedOptions);
    }, [dataType, predictedData, historicalActualDataADay, historicalPredictedDataADay, chartTitle]);

    return (
        <div id="chart">
            <ReactApexChart
                options={chartOptions}
                series={chartSeries}
                type="line"
                height={350}
            />
        </div>
    );
};

export default ApexChart;
