import React, {createContext,useState,useEffect} from 'react';
import axios from 'axios';

const DataContext = createContext();
const DataProvider = ({children}) =>{
    const [energyData,setEnergyData] = useState([]);
    const [totalEnergy,setTotalEnergy] = useState(0);
    const [predictedData,setPredictedData] = useState([]);

    const fetchData = async() =>{
        try {
            const response = await axios.post('/api/bms-data');
            setEnergyData(response.data);
          } catch (error) {
            console.error('Error fetching data:', error);
          }
    };

    // Send data to the API for prediction and store the result in the predictedData state
    const sendDataToAPI = async () => {
        try {
        const response = await axios.post('http://localhost:5000/api/predict', {
            energyData,
        });
        setPredictedData(response.data);
        } catch (error) {
        console.error('Error sending data:', error);
        }
    };

    // Calculate the total energy consumption based on the filtered data
    const calculateTotalEnergy = () => {
        let total = 0;
        for (let entry of energyData) {
        total += entry.energy;
        }
        setTotalEnergy(total);
    };

     // Fetch data and send it to the API when the component mounts or when energyData changes
    useEffect(() => {
        sendDataToAPI();
        calculateTotalEnergy();
    }, [energyData]);

    // Define the context value
    const contextValue = {
        energyData,
        totalEnergy,
        predictedData,
    };
    // Render the children components with the context value
     return <DataContext.Provider value={contextValue}>{children}</DataContext.Provider>;  
}
export { DataContext, DataProvider };