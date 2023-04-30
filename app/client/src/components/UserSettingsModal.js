import React from 'react'
import './UserSettingsModal.css'


const UserSettingsModal = (props) => {
    return (
        <div className='UserSettingsModal' onClick={() => {props.setShowUserSettings(false)}}>
            <div className='user-settings' onClick={(e) => {e.stopPropagation()}}>
                <h3>Настройки</h3>
                <div className='settings-wrapper'>
                    <div onClick={() => props.setShowFolderPreferences(true)}>Выбор папок</div>
                    <div>Еще одна настройка</div>
                </div>

            </div>
        </div>
    )
}

export default UserSettingsModal