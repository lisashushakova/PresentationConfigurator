import defaultFolderIcon from "../icons/folder.svg";
import React, {useEffect, useRef, useState} from "react";
import './SelectFolderModal.css'

const Folder = (props) => {
    const folderName = props.folderObj.name

    return (<div className='Folder'>
        <img src={defaultFolderIcon}
            onClick={() => {
                props.setFolders(props.folderObj.children)
                props.setFolderStack((prev) => [...prev, props.folderObj])
            }}
        />
        <div className='folder-name'>{folderName}</div>
    </div>)
}

const SelectFolderModal = (props) => {

    const [userFileTreeLoaded, setUserFileTreeLoaded] = useState(false)

    const [folders, setFolders] = useState([])
    const [folderStack, setFolderStack] = useState([])

    const [path, setPath] = useState('')

    useEffect(() => {
        setUserFileTreeLoaded(props.userFileTree !== null)
    }, [props.userFileTree])

    useEffect(() => {
        if (userFileTreeLoaded) {
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
        <div className='SelectFolderModal' onClick={(e) => {
            e.stopPropagation()
            props.setShowSelectFolder(false)
        }}>
            <div className='select-folder' onClick={(e) => e.stopPropagation()}>
                <h3>
                    Выбор папок
                </h3>
                <h4>{path}</h4>
                {userFileTreeLoaded ?
                    <div className='folder-list'>
                        {folders.map(folder => <Folder
                            folderObj={folder}
                            setFolders={setFolders}
                            setFolderStack={setFolderStack}
                        />)}
                    </div>
                    :
                    <div className='loading'>
                        Загрузка...
                    </div>
                }
                <div>
                    <button onClick={() => {
                        props.setSaveTo(folderStack.at(-1))
                        props.setShowSelectFolder(false)
                    }}>
                        Ок
                    </button>
                    <button onClick={() => {
                        if (userFileTreeLoaded && folderStack.length > 1) {
                            setFolderStack(prev => prev.slice(0, prev.length - 1))
                        }
                    }}>
                        Назад
                    </button>
                </div>
            </div>
        </div>
    )
}

export default SelectFolderModal