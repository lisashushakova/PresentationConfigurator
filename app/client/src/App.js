import React from 'react'
import './App.css';
import {useEffect, useLayoutEffect, useState} from 'react'
import AppHeader from './components/AppHeader'
import AppSidebar from "./components/AppSidebar";
import UserTagsModal from "./components/UserTagsModal";
import UserSettingsModal from "./components/UserSettingsModal";
import TagView from "./components/TagView";
import FolderPreferencesModal from "./components/FolderPreferencesModal";
import PresentationTagsModal from "./components/PresentationTagsModal";
import BuildView from "./components/BuildView";
import ImportSlidesModal from "./components/ImportSlidesModal";
import {wait} from "@testing-library/user-event/dist/utils";
import {waitFor} from "@testing-library/react";

export const AppMode = {
    TAG_MARKUP: 0,
    PRESENTATION_BUILD: 1
}
function App() {

    const [appMode, setAppMode] = useState(AppMode.TAG_MARKUP)
    const [userFileTree, setUserFileTree] = useState(null)
    const [created, setCreated] = useState([])
    const [modified, setModified] = useState([])

    let waitForResponse = false

    const updateFolders = () => {
        setUserFileTree(null)
        fetch('http://localhost:8000/files/tree?' + new URLSearchParams({only_folders: true}),
            {credentials: "include"})
            .then(res => res.json())
            .then(setUserFileTree)
    }

    const updateFiles = () => {
        setUserFileTree(null)
        updateFolders()
        waitForResponse = true
        fetch('http://localhost:8000/files/tree', {credentials: "include"})
            .then(res => res.json())
            .then(() => {waitForResponse = false})
        getSyncStatus()
    }

    const getSyncStatus = () => {
        fetch('http://localhost:8000/files/sync-status', {credentials: "include"})
            .then(res => res.json())
            .then(colorFileTree)
            .then(() => {
                if (waitForResponse) {
                    setTimeout(getSyncStatus, 2000)
                }
            })
    }

    useEffect(() => {
        console.log(created, modified)
    }, [created, modified])

    useEffect(() => {
        updateFiles()
    }, [])

    const colorFileTree = ((sync_data) => {
        setCreated(sync_data.created.map(pres => pres.id))
        setModified(sync_data.modified.map(pres => pres.id))
    })


    // Modal states
    const [showUserTags, setShowUserTags] = useState(false)
    const [showUserSettings, setShowUserSettings] = useState(false)
    const [showFolderPreferences, setShowFolderPreferences] = useState(false)


    return (
        <div className="App">
            <AppHeader
                setShowUserTags={setShowUserTags}
                setShowUserSettings={setShowUserSettings}
                setShowFolderPreferences={setShowFolderPreferences}
            />
            <div className='content-wrapper'>
                <AppSidebar
                    appMode={appMode}
                    setTagMode={() => {
                        setAppMode(AppMode.TAG_MARKUP)
                    }}
                    setBuildMode={() => setAppMode(AppMode.PRESENTATION_BUILD)}
                />
                {appMode === AppMode.TAG_MARKUP ?
                    <TagView
                        userFileTree={userFileTree}
                        updateFiles={updateFiles}
                        created={created}
                        modified={modified}
                    /> :
                    <BuildView userFileTree={userFileTree}/>}
            </div>

            {showUserTags ? <UserTagsModal setShowUserTags={setShowUserTags}/> : null}
            {showUserSettings ? <UserSettingsModal
                setShowUserSettings={setShowUserSettings}
                setShowFolderPreferences={setShowFolderPreferences}
            /> : null}
            {showFolderPreferences ? <FolderPreferencesModal
                userFileTree={userFileTree}
                updateFolders={updateFolders}
                updateFiles={updateFiles}
                setShowFolderPreferences={setShowFolderPreferences}
            /> : null}


        </div>
    );
}

export default App;

