import React from 'react'
import './UserTagsModal.css'
import {useEffect, useState} from "react";

const UserTagsModal = (props) => {

    const [presentationsTags, setPresentationsTags] = useState([])
    const [slidesTags, setSlidesTags] = useState([])


    useEffect(() => {
        (async () => {
            await fetch('http://localhost:8000/tags/tags-list',
                {credentials: "include"})
                .then(res => res.json())
                .then(data => {
                    console.log(data)
                    setPresentationsTags(data.presentations_tags)
                    setSlidesTags(data.slides_tags)
                })
        })()
    }, [])

    return (
        <div className='UserTagsModal' onClick={() => {props.setShowUserTags(false)}}>
            <div className='user-tags' onClick={(e) => {e.stopPropagation()}}>
                <h3>Теги пользователя</h3>
                <div className='tag-table'>
                    <div className='column'>
                        <h4>Презентации</h4>
                        {presentationsTags.map(tag => <div>{tag.name}</div>)}
                    </div>
                    <div className='column'>
                        <h4>Слайды</h4>
                        {slidesTags.map(tag => <div>{tag.name}</div>)}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default UserTagsModal