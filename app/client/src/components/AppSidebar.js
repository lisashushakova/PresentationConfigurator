import React from 'react'
import './AppSidebar.css'

const SideBar = (props) => {
    return (
        <div className="AppSidebar">
            <button onClick={props.setTagMode}>Разметка тегов</button>
            <button onClick={props.setBuildMode}>Сборка презентации</button>
        </div>
    )
}

export default SideBar