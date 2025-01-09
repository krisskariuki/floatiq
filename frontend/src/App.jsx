import { useState } from 'react'
import './styles/utils.css'
import './styles/App.css'

import Header from './components/Header'
import Navbar from './components/Navbar'
import Dashboard from './components/Dashboard'

export default function App() {
  return (
    <>
    <Header/>
    <Navbar/>
    <Dashboard/>
    </>
  )
}
