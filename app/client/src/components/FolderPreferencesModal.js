import React from 'react'
import './FolderPreferencesModal.css'
import defaultFolderIcon from '../icons/folder.svg'
import markedFolderIcon from '../icons/folder-full-pref.svg'
import hasMarkedChildFolderIcon from '../icons/folder-sub-pref.svg'
import reloadIcon from '../icons/refresh.svg'


import {useEffect, useState} from "react";

const FolderMarks = {
    DEFAULT: 0,
    MARKED: 1,
    HAS_MARKED_CHILD: 2
}

const Folder = (props) => {
    const folderName = props.folderObj.name
    const folderId = props.folderObj.id
    const folderMark = props.folderObj.extendedMark

    useEffect(() => {

    }, [props.folderObj])

    let imgSrc = null

    switch (folderMark) {
        case FolderMarks.DEFAULT:
            imgSrc = defaultFolderIcon
            break

        case FolderMarks.MARKED:
            imgSrc = markedFolderIcon
            break

        case FolderMarks.HAS_MARKED_CHILD:
            imgSrc = hasMarkedChildFolderIcon
            break

    }

    return (<div className='Folder'>
        <img src={imgSrc}
            onClick={() => {
                props.setFolders(props.folderObj.children)
                props.setFolderStack((prev) => [...prev, props.folderObj])
            }}


            onContextMenu={(e) => {
                e.preventDefault()
                const newMark = !props.folderObj.mark
                const propagate = (node, value) => {
                    node.mark = value
                    fetch("http://localhost:8000/files/folders/set-mark?" +
                        new URLSearchParams({folder_id: node.id, value: value}),
                        {method: "POST", credentials: "include"})
                    node.children
                        .filter(child => child.type === 'folder')
                        .map(child => propagate(child, value))

                }

                propagate(props.folderObj, newMark)

                props.updateMarks()
            }}
        />
        <div className='folder-name'>{folderName}</div>
    </div>)
}

const FolderPreferencesModal = (props) => {

    const [userFileTreeLoaded, setUserFileTreeLoaded] = useState(false)

    const [folders, setFolders] = useState([])
    const [folderStack, setFolderStack] = useState([])

    const [path, setPath] = useState('')

    const updateMarks = () => {
        const traverse = (node) => {
            if (node.type === 'folder') {
                // Categorize marks of folders
                if (node.mark) {
                    node.extendedMark = FolderMarks.MARKED
                    node.children.map(child => traverse(child))
                    return true
                } else {
                    const result = node.children.map((child) => traverse(child))
                    if (result.some(child => child)) {
                        node.extendedMark = FolderMarks.HAS_MARKED_CHILD
                        return true
                    } else {
                        node.extendedMark = FolderMarks.DEFAULT
                        return false
                    }

                }
            }
        }
        traverse(props.userFileTree)
        setFolderStack([...folderStack])
    }

    useEffect(() => {
        setUserFileTreeLoaded(props.userFileTree !== null)
    }, [props.userFileTree])

    useEffect(() => {
        if (userFileTreeLoaded) {
            updateMarks()
            setFolderStack([props.userFileTree])
        }

    }, [userFileTreeLoaded])


    useEffect(() => {
        if (userFileTreeLoaded) {
            setFolders(folderStack.at(-1).children.filter(element => element.type === 'folder')
                .map(element => {
                    element.key = element.id
                    return element
                }
            ))
        }
        let newPath = ''
        for (const stackElement of folderStack) {
            newPath += stackElement.name + '/'
        }
        setPath(newPath)
    }, [folderStack])

    return (
        <div className='FolderPreferencesModal' onClick={() => {
            props.updateFiles()
            props.setShowFolderPreferences(false)
        }}>
            <div className='folder-preferences' onClick={(e) => {e.stopPropagation()}}>
                <h3>
                    Выбор папок
                    <button onClick={(e) => {
                        setUserFileTreeLoaded(false)
                        props.updateFolders()
                    }}>
                        <img src={reloadIcon}/>
                    </button>
                </h3>
                <h4>{path}</h4>
                {userFileTreeLoaded ?
                    <div className='folder-list'>
                        {folders.map(folder => <Folder
                            folderObj={folder}
                            setFolders={setFolders}
                            setFolderStack={setFolderStack}
                            updateMarks={updateMarks}
                        />)}
                    </div>
                    :
                    <div className='loading'>
                        Загрузка...
                    </div>
                }
                {userFileTreeLoaded && folderStack.length > 1 ? <button onClick={() => {
                    setFolderStack(prev => prev.slice(0, prev.length - 1))
                }}>Назад</button> : null}
            </div>
        </div>
    )
}

export default FolderPreferencesModal