import './SelectPresentationMenu.css'
import refreshIcon from '../icons/refresh.svg'
import React, {createRef, useEffect, useRef, useState} from 'react'

const MenuObjectType = {
    ROOT_FOLDER: 0,
    FOLDER: 1,
    PRESENTATION: 2
}

const MenuObject = (props) => {

    let className = 'MenuObject'
    let headerElement = null

    switch (props.obj.menuObjectType) {
        case MenuObjectType.ROOT_FOLDER:
            className += ' root-folder'
            headerElement = <h3>{props.obj.name}</h3>
            break
        case MenuObjectType.FOLDER:
            className += ' folder'
            headerElement = <h4>{props.obj.name}</h4>
            break
        case MenuObjectType.PRESENTATION:
            className += ' presentation'
            headerElement = <h5>{props.obj.name}</h5>
            break
    }

    if (props.obj.status) {
        className += ' ' + props.obj.status
    }


    return (props.obj.show ?
        <div className={className} onClick={(e) => {
            e.stopPropagation()
            if (props.obj.menuObjectType === MenuObjectType.PRESENTATION) {
                props.setSelectedPresentation(props.obj)
                props.setShowSelectPresentation(false)
            }
        }}>
            {headerElement}
            {props.obj.children ? props.obj.children.map(child => <MenuObject
                    obj={child}
                    setSelectedPresentation={props.setSelectedPresentation}
                    setShowSelectPresentation={props.setShowSelectPresentation}
                />) : null}
        </div>
        :
        null
    )
}

const SelectPresentationMenu = (props) => {

    return (
        <div className='SelectPresentationMenu'>
            {props.processedUserFileTree ?
                <>
                    <div className={'pres-search'}>
                        <h3>Поиск по презентациям</h3>
                        <div>
                            <input type="text" placeholder="Поиск..." value={props.searchFieldValue} onChange={
                                (e) => props.setSearchFieldValue(e.target.value)
                            }/>
                            <div className='radio-wrapper'>
                                <input id="pres-search-name" name="search-type" type="radio" value="name"
                                       defaultChecked={props.searchMode === "name"} onChange={
                                    (e) => props.setSearchMode(e.target.value)
                                }/>
                                <label htmlFor="pres-search-name">Имя</label>
                            </div>
                            <div className='radio-wrapper'>
                                <input id="pres-search-tags" name="search-type" type="radio" value="tags"
                                       defaultChecked={props.searchMode === "tags"} onChange={
                                           (e) => props.setSearchMode(e.target.value)
                                       }/>
                                <label htmlFor="pres-search-tags">Теги</label>
                            </div>
                        </div>
                    </div>
                    {
                        props.processedUserFileTree ?
                            <MenuObject
                                obj={props.processedUserFileTree}
                                setSelectedPresentation={props.setSelectedPresentation}
                                setShowSelectPresentation={props.setShowSelectPresentation}
                            /> : null
                    }
                    <button onClick={props.updateFiles}><img src={refreshIcon}/></button>
                </>
                :
                <div className="loading">Загрузка...</div>
            }
        </div>
    )

}

export {SelectPresentationMenu, MenuObjectType}