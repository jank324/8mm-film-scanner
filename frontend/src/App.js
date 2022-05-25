import React, { useState, useEffect } from "react"
import axios from "axios"

import './App.css';


const flask = route => "http://192.168.178.48:5000" + route


function App() {

  return (
    <div className="grid grid-cols-1 sm:flex w-screen">
      <Preview />
      <Controls />
    </div>
  )
}


const Preview = () => {
  return (
    <div className="grow shrink justify-center flex bg-black">
      <img className="w-screen sm:w-auto sm:h-screen object-contain" src={flask("/preview")} alt="Preview of the current frame"></img>
    </div>
  )
}


const Controls = () => {

  const [isScanning, setIsScanning] = useState(false)
  const [outputDirectory, setOutputDirectory] = useState("")
  const [nFrames, setNFrames] = useState(3800)
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0)
  const [lastScanEndInfo, setLastScanEndInfo] = useState("dismissed")
  const [timeRemaining, setTimeRemaining] = useState("-")
  const [isShowingPoweroffModal, setIsShowingPoweroffModal] = useState(false)

  useEffect(() => {
    axios.get(flask("/scan")).then(response => {
      setIsScanning(response.data.is_scanning)
      setOutputDirectory(response.data.output_directory)
      setNFrames(response.data.n_frames)
      setLastScanEndInfo(response.data.last_scan_end_info)
      setTimeRemaining(response.time_remaining)
    })

    const sse = new EventSource(flask("/scan-stream"))
    sse.addEventListener("is_scanning", e => setIsScanning(e.data === "True"))
    sse.addEventListener("output_directory", e => setOutputDirectory(e.data))
    sse.addEventListener("n_frames", e => setNFrames(parseInt(e.data)))
    sse.addEventListener("current_frame_index", e => setCurrentFrameIndex(parseInt(e.data)))
    sse.addEventListener("last_scan_end_info", e => setLastScanEndInfo(e.data))
    sse.addEventListener("time_remaining", e => setTimeRemaining(e.data))
    sse.onerror = e => sse.close()  // TODO: Do something more intelligent

    return () => sse.close()
  }, [])

  const scanButtonStartStyle = "bg-green-700 border-green-700 hover:bg-green-800 hover:border-green-800 focus:ring-green-300 dark:bg-green-600 dark:border-green-600 dark:hover:bg-green-700 dark:hover:border-green-700 dark:focus:ring-green-800"
  const scanButtonStopStyle = "bg-red-700 border-red-700 hover:bg-red-800 hover:border-red-800 focus:ring-red-300 dark:bg-red-600 dark:border-red-600 dark:hover:bg-red-700 dark:hover:border-red-700 dark:focus:ring-red-900"

  const startScan = () => axios.post(flask("/scan"), {output_directory: outputDirectory, n_frames: nFrames})
  const poweroff = () => axios.post(flask("/poweroff"))   // TODO blank out screen or something

  const openPoweroffModal = () => setIsShowingPoweroffModal(true)
  const closePoweroffModal = () => setIsShowingPoweroffModal(false)

  const onOutputDirectoryChange = event => setOutputDirectory(event.target.value)
  const onNFramesChange = event => setNFrames(event.target.value)

  return (
    <div className="lg:w-80 shrink-0 m-0 p-2 flex flex-col bg-white dark:bg-gray-800">
      <ButtonGrid>
        <Toggle target={flask("/advance")}>🦦 Step</Toggle>
        <Toggle target={flask("/light")}>💡 Light</Toggle>
        <Toggle target={flask("/fastforward")}>🏎 Fast-Forward</Toggle>
        <Toggle target={flask("/focuszoom")}>🔍 Zoom</Toggle>
      </ButtonGrid>

      <ProgressBar now={currentFrameIndex + isScanning} max={nFrames} info={timeRemaining} show={isScanning} />
      <ScanSuccessAlert show={lastScanEndInfo === "success"} />
      <ScanFailureAlert show={lastScanEndInfo === "failure"} />

      <div className="mt-2">
        <label htmlFor="n_frames" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">Reel length</label>
        <input type="text" id="n_frames" className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Number of frames" value={nFrames} required disabled={isScanning} onChange={onNFramesChange} />
      </div>
      <div className="mt-2">
        <label htmlFor="output_directory" className="block mb-2 text-sm font-medium text-gray-900 dark:text-gray-300">Output directory</label>
        <input type="text" id="output_directory" className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Directory to save scanned files to" value={outputDirectory} required disabled={isScanning} onChange={onOutputDirectoryChange} />
      </div>
      <button type="button" className={"mt-4 focus:outline-none text-white focus:ring-4 font-medium rounded-lg text-sm px-5 py-2.5 border " + (isScanning? scanButtonStopStyle : scanButtonStartStyle)} onClick={startScan}>{isScanning ? "⏹ Stop" : "🎥 Scan"}</button>

      <div className="flex flex-col-reverse justify-start items-end flex-grow">
        <button className="mt-4 text-gray-900 bg-white hover:bg-gray-100 border border-gray-200 focus:ring-4 focus:outline-none focus:ring-gray-100 font-medium rounded-lg text-sm px-4 py-2.5 text-center inline-flex items-center dark:focus:ring-gray-600 dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:hover:bg-gray-700 flex-grow-0 disabled:text-gray-400 disabled:hover:bg-white dark:disabled:text-gray-500 dark:disabled:hover:bg-gray-800 disabled:cursor-not-allowed" onClick={openPoweroffModal} disabled={isScanning}>😴 Power off</button>
      </div>
      <PoweroffModal onConfirm={poweroff} onAbort={closePoweroffModal} show={isShowingPoweroffModal} />
    </div>
  )
}


const ButtonGrid = ({children}) => {
  return (
    <div className="grid grid-cols-2 gap-2 pb-2 border-b-2 border-gray-200 dark:border-gray-700">
      {children}
    </div>
  )
}


const Toggle = ({children, target}) => {

  const [isEnabled, setIsEnabled] = useState(true)
  const [isActive, setIsActive] = useState(false)

  useEffect(() => {
    axios.get(target).then(response => {
      setIsEnabled(response.data.is_enabled)
      setIsActive(response.data.is_active)
    })

    const sse = new EventSource(target + "-stream")
    sse.addEventListener("is_enabled", e => setIsEnabled(e.data === "True"))
    sse.addEventListener("is_active", e => setIsActive(e.data === "True"))
    sse.onerror = e => sse.close()  // TODO: Do something more intelligent

    return () => sse.close()
  }, [target])

  const toggle = () => axios.post(target)

  const activeStyle = "border-yellow-400 dark:border-yellow-400"
  const inactiveStyle = "border-gray-200 dark:border-gray-700"

  return (
    <button className={"text-gray-900 bg-white hover:bg-gray-100 border focus:ring-4 focus:outline-none focus:ring-gray-100 font-medium rounded-lg text-sm px-4 py-2.5 text-center inline-flex items-center dark:focus:ring-gray-600 dark:bg-gray-800 dark:text-white dark:hover:bg-gray-700 disabled:text-gray-400 disabled:hover:bg-white dark:disabled:text-gray-500 dark:disabled:hover:bg-gray-800 disabled:cursor-not-allowed cursor-pointer " + (isActive ? activeStyle : inactiveStyle)} onClick={toggle} disabled={!isEnabled}>{children}</button>
  )
}

const ProgressBar = ({max, now, info, show}) => {

  const showStyle = "p-4 mt-2"
  const hiddenStyle = "h-0 p-0"

  return (
    <div className={"p-4 text-sm text-gray-700 bg-gray-100 rounded-lg dark:bg-gray-700 dark:text-gray-300 overflow-hidden transition-all " + (show ? showStyle : hiddenStyle)} role="alert">
      <span className="font-medium">Scanning ...</span>
      <div className="flex justify-between mb-1">
        <span className="text-sm text-purple-500 dark:text-purple-400">Frame {now} of {max}</span>
        <span className="text-sm text-purple-500 dark:text-purple-400">{info}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-1.5 dark:bg-gray-900">
        <div className="bg-purple-500 dark:bg-purple-400 h-1.5 rounded-full transition-all" style={{width: `${now / max * 100}%`}}></div>
      </div>
    </div>
  )
}

const ScanSuccessAlert = ({show}) => {

  const dismiss = () => axios.post(flask("/dismiss"))

  const showStyle = "p-4 mt-2"
  const hiddenStyle = "h-0 p-0"

  return (
    <div className={"flex bg-green-100 rounded-lg dark:bg-green-200 overflow-hidden transition-all " + (show ? showStyle : hiddenStyle)} role="alert">
      <svg className="flex-shrink-0 w-5 h-5 text-green-700 dark:text-green-800" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"></path></svg>
      <div className="flex-col ml-3 text-sm font-medium text-green-700 dark:text-green-800">
        Scan finished successfully!
      </div>
      <button type="button" onClick={dismiss} className="ml-auto -mx-1.5 -my-1.5 bg-green-100 text-green-500 rounded-lg focus:ring-2 focus:ring-green-400 p-1.5 hover:bg-green-200 inline-flex h-8 w-8 dark:bg-green-200 dark:text-green-600 dark:hover:bg-green-300" aria-label="Close">
        <span className="sr-only">Close</span>
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"></path></svg>
      </button>
    </div>
  )
}

const ScanFailureAlert = ({show}) => {

  const dismiss = () => axios.post(flask("/dismiss"))

  const showStyle = "p-4 mt-2"
  const hiddenStyle = "h-0 p-0"

  return (
    <div className={"flex bg-red-100 rounded-lg dark:bg-red-200 overflow-hidden transition-all " + (show ? showStyle : hiddenStyle)} role="alert">
      <svg className="flex-shrink-0 w-5 h-5 text-red-700 dark:text-red-800" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"></path></svg>
      <div className="ml-3 text-sm font-medium text-red-700 dark:text-red-800">
        Scan failed!
      </div>
      <button type="button" onClick={dismiss} className="ml-auto -mx-1.5 -my-1.5 bg-red-100 text-red-500 rounded-lg focus:ring-2 focus:ring-red-400 p-1.5 hover:bg-red-200 inline-flex h-8 w-8 dark:bg-red-200 dark:text-red-600 dark:hover:bg-red-300" aria-label="Close">
        <span className="sr-only">Close</span>
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"></path></svg>
      </button>
    </div>
  )
}

const PoweroffModal = ({onConfirm, onAbort, show}) => {

  return (
    <div tabIndex="-1" className={"fixed top-0 right-0 left-0 w-full h-full flex bg-[#000000AA] " + (show ? "block" : "hidden")}>
      <div className="relative w-96 m-auto align-middle rounded-lg shadow bg-white dark:bg-gray-800">
        <button onClick={onAbort} className="absolute top-3 right-2.5 text-gray-400 bg-transparent hover:bg-gray-100 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center dark:hover:bg-gray-700 dark:hover:text-white">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"></path></svg>  
        </button>
        <div className="px-12 py-6 flex-col text-center">
          <h3 className="mb-5 text-lg font-normal text-gray-900 dark:text-white">Are you sure you want to turn off the scanner?</h3>
          <button onClick={onConfirm} className="text-white border bg-red-600 border-red-600 hover:bg-red-800 hover:border-red-800 focus:ring-4 focus:outline-none focus:ring-red-300 dark:focus:ring-red-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 w-[106px]">Power off</button>
          <button onClick={onAbort} className="text-gray-900 bg-white hover:bg-gray-100 border focus:ring-4 focus:outline-none focus:ring-gray-100 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:focus:ring-gray-600 dark:bg-gray-800 dark:text-white dark:hover:bg-gray-700 cursor-pointer border-gray-200 dark:border-gray-700 w-[106px]">Cancel</button>
        </div>
      </div>
    </div>
  )
}

export default App;
