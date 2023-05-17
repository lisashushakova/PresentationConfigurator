import React, {useEffect, useState} from 'react'
import './AppSidebar.css'
import {AppMode} from "../App";

const SideBar = (props) => {
    const [tagBtnStyle, setTagBtnStyle] = useState('')
    const [buildBtnStyle, setBuildBtnStyle] = useState('')

    useEffect(() => {
        if (props.appMode === AppMode.TAG_MARKUP) {
            setTagBtnStyle('selected')
            setBuildBtnStyle('')
        } else {
            setTagBtnStyle('')
            setBuildBtnStyle('selected')
        }
    }, [props.appMode])

    return (
        <div className="AppSidebar">
            <button className={tagBtnStyle} onClick={props.setTagMode}>Разметка тегов</button>
            <button className={buildBtnStyle} onClick={props.setBuildMode}>Сборка презентации</button>
        </div>
    )
}

export default SideBar