import React, { createContext, useState, useEffect } from "react";
import axios from "axios";
import Echo from 'laravel-echo';
import io from 'socket.io-client';
import { format, startOfMinute, addMinutes } from 'date-fns';
import { utcToZonedTime } from 'date-fns-tz';

const DataContext = createContext();

const DataProvider = ({ children }) => {
    const [predictedData, setPredictedData] = useState([]);
    const [actualData, setActualData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null); // Add error state
    const [date,setDate]=useState(new Date());
    const [historicalActualDataADay, setHistoricalActualDataADay] = useState([]);
    const [historicalPredictedDataADay, setHistoricalPredictedDataADay] = useState([]);    
    const [historicalActualDataTwoDays, setHistoricalActualDataTwoDays] = useState([]);
    const [historicalPredictedDataTwoDays, setHistoricalPredictedDataTwoDays] = useState([]);
    const [mapeThreshold, setMapeThreshold] = useState(20);
    
     // Set a timeout to update isLoading to false if no data arrives within 10 seconds
  useEffect(() => {
    const timeout = setTimeout(() => {
      setIsLoading(false);
    }, 5000); // 10 seconds
    
    return () => {
      clearTimeout(timeout); // Clear the timeout when the component unmounts
    };
  }, []);
//for loading the previous data if there is no data incoming at that time
useEffect(() => {
  // const date = new Date("2023-03-03T23:40:00");
  if(date.getDate() < new Date()){
    date.setHours(23,35,0);
  }
  const currentTime = date.getHours() * 60 + date.getMinutes(); // Convert current time to minutes
  const roundedTime = Math.floor(currentTime / 30) * 30; // Round down to nearest 30-minute interval
 
  const cutoffTimeUTC = startOfMinute(addMinutes(date, -currentTime % 30)); // Subtract the remainder to round down
  const cutoffTimeMinusOneDayUTC = new Date(cutoffTimeUTC); // Create a new date object based on cutoffTimeUTC
  const cutoffTimeMinusTwoDaysUTC = new Date(cutoffTimeUTC); // Create a new date object based on cutoffTimeUTC
  cutoffTimeMinusOneDayUTC.setDate(cutoffTimeMinusOneDayUTC.getDate() - 1);
  cutoffTimeMinusTwoDaysUTC.setDate(cutoffTimeMinusTwoDaysUTC.getDate() - 2);

  // Convert the UTC cutoff time to local timezone
  const localTimeZone = 'Asia/Singapore'; 
  const cutoffTime = utcToZonedTime(cutoffTimeUTC, localTimeZone); 
  const cutoffTimeMinusOneDay = utcToZonedTime(cutoffTimeMinusOneDayUTC,localTimeZone);
  const cutoffTimeMinusTwoDays = utcToZonedTime(cutoffTimeMinusTwoDaysUTC,localTimeZone);
  console.log(cutoffTime,cutoffTimeMinusOneDay);
  // Format cutoffTime as YYYY-MM-DD HH:MM:SS
  const formattedCutoffTime = format(cutoffTime, "yyyy-MM-dd'T'HH:mm:ss");
  const formattedCutoffTimeMinusOneDay = format(cutoffTimeMinusOneDay, "yyyy-MM-dd'T'HH:mm:ss");
  const formattedCutoffTimeMinusTwoDays = format(cutoffTimeMinusTwoDays, "yyyy-MM-dd'T'HH:mm:ss");


  Promise.all([
    // axios.post('/api/get-data/actual', { 'Date/Time': formattedCutoffTime }),
    axios.post('/api/get-data/predict', { 'Date/Time': formattedCutoffTime }),
    axios.post('/api/get-data/actual', { 'Date/Time': formattedCutoffTimeMinusOneDay}),
    axios.post('/api/get-data/predict', { 'Date/Time': formattedCutoffTimeMinusOneDay }),
    axios.post('/api/get-data/actual', { 'Date/Time': formattedCutoffTimeMinusTwoDays}),
    axios.post('/api/get-data/predict', { 'Date/Time': formattedCutoffTimeMinusTwoDays }),
  ])
    .then(([predicted_data_response,
      historical_actual_data_response_a_day,
      historical_predicted_data_response_a_day,
      historical_actual_data_response_two_days,
      historical_predicted_data_response_two_days]) => {

      setPredictedData(predicted_data_response.data);
      setHistoricalActualDataADay(historical_actual_data_response_a_day.data);
      setHistoricalActualDataTwoDays(historical_actual_data_response_two_days.data);
      setHistoricalPredictedDataADay(historical_predicted_data_response_a_day.data);
      setHistoricalPredictedDataTwoDays(historical_predicted_data_response_two_days.data);
      setIsLoading(false);
    })
    .catch(error => {
      setError("Error fetching data: " + error.message);
      setIsLoading(false);
    });
}, [date]);


  useEffect(() => {
    Pusher.logToConsole = true;
  
    var pusher = new Pusher(import.meta.env.VITE_PUSHER_APP_KEY, {
      cluster: import.meta.env.VITE_PUSHER_APP_CLUSTER,
      forceTLS: true,
    });
  
    var channel = pusher.subscribe('public-channel');
    channel.bind('event_apidata', async function (data) {
      console.log("Before HTTP actual:", data.data.actual_data);
  
      // Use Promise.all to wait for both API calls to complete
      const [actual_data_response, predicted_data_response] = await Promise.all([
        axios.post('/api/get-data/actual', { 'Date/Time': data.data.actual_data[0]['Date/Time'] }),
        axios.post('/api/get-data/predict', { 'Date/Time': data.data.actual_data[0]['Date/Time'] })
      ]);

      setActualData(actual_data_response.data);
      setPredictedData(predicted_data_response.data);
      setIsLoading(false);
    });
  }, []);
    
    // Show loading state or error message until data is available
    if (isLoading) {
      return <div>Loading...</div>;
    }
  
    if (error) {
      return <div>{error}</div>;
    }
  
    // Define the context value
    const contextValue = {
      predictedData,
      actualData,
      date,
      setDate,
      historicalActualDataADay, 
      historicalPredictedDataADay,      
      historicalActualDataTwoDays, 
      historicalPredictedDataTwoDays,
      mapeThreshold,
    };
  
    return (
      <DataContext.Provider value={contextValue}>
        {children}
      </DataContext.Provider>
    );
  };
  
  export { DataContext, DataProvider };