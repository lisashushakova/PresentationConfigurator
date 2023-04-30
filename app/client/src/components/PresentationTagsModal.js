import React from 'react'
import './PresentationTagsModal.css'
import TagTable from "./TagTable";
import {useEffect, useRef} from "react";

const PresentationTagsModal = (props) => {

    const tagTableRef = useRef()

    useEffect(() => {
        if (props.selectedPresentation) {
            fetch('http://localhost:8000/links/presentation-links?' + new URLSearchParams({
                presentation_id: props.selectedPresentation.id
            }),{
                credentials: 'include'
            }).then(res => res.json()).then(((data) => tagTableRef.current.updateTable(data.links)))
        }
    }, [props.selectedPresentation])

    const createPresentationTagCallback = (tag_name, value) => {
        fetch('http://localhost:8000/links/create-presentation-link?' + new URLSearchParams({
            presentation_id: props.selectedPresentation.id,
            tag_name: tag_name,
            value: value
        }),{
            method: 'POST',
            credentials: 'include'
        })
    }

    const removePresentationTagCallback = (tag_name) => {
        fetch('http://localhost:8000/links/remove-presentation-link?' + new URLSearchParams({
            presentation_id: props.selectedPresentation.id,
            tag_name: tag_name,
        }),{
            method: 'POST',
            credentials: 'include'
        })
    }

    return (
        <div className='PresentationTagsModal' onClick={() => props.setShowPresentationTags(false)}>
            <div className='presentation-tags' onClick={(e) => e.stopPropagation()}>
                <h3>Теги презентации</h3>
                <TagTable
                    ref={tagTableRef}
                    createTagCallback={createPresentationTagCallback}
                    updateTagCallback={createPresentationTagCallback}
                    removeTagCallback={removePresentationTagCallback}
                />
            </div>
        </div>
    )
}

export default PresentationTagsModal