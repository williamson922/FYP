import React, { createContext, useState, useEffect } from "react";
import axios from "axios";
import Echo from 'laravel-echo';
import io from 'socket.io-client';

const DataContext = createContext();

const DataProvider = ({ children }) => {
    const [predictedData, setPredictedData] = useState([]);
    const [actualData, setActualData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null); // Add error state
    

     // Set a timeout to update isLoading to false if no data arrives within 10 seconds
  useEffect(() => {
    const timeout = setTimeout(() => {
      setIsLoading(false);
    }, 5000); // 10 seconds
    
    return () => {
      clearTimeout(timeout); // Clear the timeout when the component unmounts
    };
  }, []);

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
  
      console.log("After HTTP actual:", actual_data_response);
      console.log("After HTTP predict:", predicted_data_response);
  
      setActualData(actual_data_response.data);
      setPredictedData(predicted_data_response.data);
      setIsLoading(false);
    });
  }, []);
  
    
    if(actualData.length>0){
      console.log("Actual:");
      console.log(actualData.map(entry => (entry['Total Power']/1000).toFixed(2)));
      }

      if(predictedData.length>0){
        console.log("Predicted:");
        console.log(predictedData.map(entry => (entry['predicted power']/1000).toFixed(2)));
        }
      
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
    };
  
    return (
      <DataContext.Provider value={contextValue}>
        {children}
      </DataContext.Provider>
    );
  };
  
  export { DataContext, DataProvider };