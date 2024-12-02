import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './App.css'
import Table from './Components/Table'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<h1>Hello World</h1>} />
        <Route path="/table" element={<Table />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
