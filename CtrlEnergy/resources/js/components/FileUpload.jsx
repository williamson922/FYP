import React,{useState} from 'react';
import axios from 'axios'; 
import ApexChart from './ApexChart'
const FileUpload = () =>{
    const [selectedFile,setSelectedFile] = useState(null);
    
    const handleFileChange = (e) =>{
        setSelectedFile(e.target.files[0]);};
    
    const handleFileSubmit = async() =>{
        if (selectedFile){
            try{
                const formData = new FormData();
                formData.append('file',selectedFile);
                const res = await axios.post('http://localhost:5000/api/predict',formData,{ 
                    headers :{
                    'Content-Type':'multipart/form-data',
                },});
                console.log("upload successful")
            } catch(error){
                console.log(error)
            }
        }
    };
    return(
        <div className = "file-upload">
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleFileSubmit}>Upload File</button>
        </div>
    );}
export default FileUpload;
