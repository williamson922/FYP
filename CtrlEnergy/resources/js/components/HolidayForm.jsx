import React, { useState,useEffect } from 'react';
import axios from 'axios';

const HolidayForm = () => {
  const [holidayDate, setHolidayDate] = useState('');
  const [holidays, setHolidays] = useState([]);

  useEffect(() => {
    fetchHolidays();
  }, []);

  const handleHolidayDateChange = (e) => {
    setHolidayDate(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Send the holiday date to the server to be saved in the database
      const response = await axios.post('/api/set-holiday', { date: holidayDate });
      // Handle the response as needed
      console.log(response);
      // Clear the input field
      setHolidayDate('');
    } catch (error) {
      console.error(error);
    }
  };

  const fetchHolidays = async () => {
    try {
      const response = await axios.get('/api/holidays');
      setHolidays(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="holiday-form">
      <h2>Add Holiday Date</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="holiday-date">Holiday Date:</label>
          <input
            type="date"
            id="holiday-date"
            className="form-control"
            value={holidayDate}
            onChange={handleHolidayDateChange}
          />
        </div>
        <button type="submit" className="btn btn-primary">Add</button>
      </form>
      <div>
        <h2>Holidays</h2>
        {holidays.length > 0 ? (
          <ul className="holiday-list">
            {holidays.map((holiday) => (
              <li key={holiday.id}>{holiday.date}</li>
            ))}
          </ul>
        ) : (
          <p>No holidays found.</p>
        )}
      </div>
    </div>
  );
};
export default HolidayForm;
