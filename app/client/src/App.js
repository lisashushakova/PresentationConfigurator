import React from 'react'
import './App.css';
import {useEffect, useState} from 'react'
import AppHeader from './components/AppHeader'
import AppSidebar from "./components/AppSidebar";
import UserTagsModal from "./components/UserTagsModal";
import TagView from "./components/TagView";
import FolderPreferencesModal from "./components/FolderPreferencesModal";
import BuildView from "./components/BuildView";



export const AppMode = {
    TAG_MARKUP: 0,
    PRESENTATION_BUILD: 1
}
function App() {

    const [appMode, setAppMode] = useState(AppMode.TAG_MARKUP)
    const [userFileTree, setUserFileTree] = useState(null)
    const [created, setCreated] = useState([])
    const [modified, setModified] = useState([])
    const [synced, setSynced] = useState([])
    const [userLogged, setUserLogged] = useState(false)

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
        if (userLogged) {
            fetch('http://localhost:8000/files/sync-status', {credentials: "include"})
                .then(res => res.json())
                .then(data => {
                    console.log(data)
                    colorFileTree(data)
                })
                .then(() => {
                    if (waitForResponse) {
                        setTimeout(getSyncStatus, 2000)
                    }
                })
        }
    }


    useEffect(() => {
        if (userLogged) {
            updateFiles()
        }
    }, [userLogged])

    const colorFileTree = ((sync_data) => {
        setCreated(sync_data.created.map(pres => pres.id))
        setModified(sync_data.modified.map(pres => pres.id))
        setSynced(sync_data.synced.map(pres => pres.id))
    })


    // Modal states
    const [showUserTags, setShowUserTags] = useState(false)
    const [showFolderPreferences, setShowFolderPreferences] = useState(false)


    return (
        <div className="App">
            <AppHeader
                setShowUserTags={setShowUserTags}
                setShowFolderPreferences={setShowFolderPreferences}
                userLogged={userLogged}
                setUserLogged={setUserLogged}
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
                        synced={synced}
                    /> :
                    <BuildView userFileTree={userFileTree}/>}
            </div>

            {showUserTags ? <UserTagsModal setShowUserTags={setShowUserTags}/> : null}
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

