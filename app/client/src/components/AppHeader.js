import React from 'react'
import './AppHeader.css'
import tagsIcon from '../icons/tag.svg'
import settingsIcon from '../icons/settings.svg'
import userIcon from '../icons/user.svg'
import {useEffect, useLayoutEffect, useState} from "react";



const SelectUserMenu = (props) => {

    return (
        <div className="SelectUserMenu">
            {props.userLogged ?
                <>
                    <div>Пользователь: {props.userInfo.username}</div>
                    <button className='logoutBtn' onClick={() => fetch("http://localhost:8000/auth/logout",
                    {method: "POST", credentials: "include"})
                    .then(() => {
                        props.setUserLogged(false)
                        props.setUserInfo([])
                    })}>Выйти из аккаунта</button>
                </>

                :
                <button className='loginBtn' onClick={() => {
                    window.location.replace("http://localhost:8000/auth/login")
                }}>Войти в аккаунт</button>}
        </div>
    )
}

const AppHeader = (props) => {
    const [showSelectUser, setShowSelectUser] = useState(false)

    const [userInfo, setUserInfo] = useState({})

    useEffect(() => {
        const cookieIndex = document.cookie.indexOf('pres_conf_user_state')
        props.setUserLogged(cookieIndex !== -1)
        if (props.userLogged) {
            fetch("http://localhost:8000/auth/user-info", {credentials:"include"})
              .then(response => response.json())
              .then((data) => setUserInfo(data))
        }
    }, [props.userLogged])


    return (
        <div className="AppHeader">
            <div>Конфигуратор презентаций</div>
            <div className={'button-block'}>
                <button><img
                    src={tagsIcon}
                    alt={"Tags"}
                    onClick={() => {props.setShowUserTags(true)}}/>
                </button>

                <button><img
                    src={settingsIcon}
                    alt={"Settings"}
                    onClick={() => {props.setShowFolderPreferences(true)}}/>
                </button>

                <button
                    onClick={() => setShowSelectUser(prev => !prev)}
                    onBlur={(e) => {
                        if (!(e.relatedTarget && (['loginBtn', 'logoutBtn'].includes(e.relatedTarget.className)))) {
                            setShowSelectUser(false)
                        }
                    }}
                >
                    <img src={userInfo.iconURL ? userInfo.iconURL : userIcon} alt={"Users"} />
                </button>


            </div>
            {showSelectUser ? <SelectUserMenu
                userLogged={props.userLogged}
                setUserLogged={props.setUserLogged}
                userInfo={userInfo}
                setUserInfo={setUserInfo}
            /> : null}
        </div>

    )


}

export default AppHeader