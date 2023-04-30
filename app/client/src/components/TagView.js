import React, { Component } from 'react'
import './TagView.css'
import {SlideCard, SlideRatio} from "./SlideCard";
import TagTable from "./TagTable";
import {useEffect, useRef, useState} from "react";
import {SelectPresentationMenu, MenuObjectType} from "./SelectPresentationMenu";
import PresentationTagsModal from "./PresentationTagsModal";

const TagView = (props) => {

    const [showSelectPresentation, setShowSelectPresentation] = useState(false)


    const selectPresentationMenuRef = useRef()

    const [selectedPresentation, setSelectedPresentation] = useState(null)
    const [selectedPresentationSlides, setSelectedPresentationSlides] = useState([])

    const [selectedSlide, setSelectedSlide] = useState(null)

    const [processedUserFileTree, setProcessedUserFileTree] = useState(null)

    const [searchFieldValue, setSearchFieldValue] = useState('')
    const [searchMode, setSearchMode] = useState('name')

    const tagTableRef = useRef()

    const [showPresentationTags, setShowPresentationTags] = useState(false)

    const createSlideTagCallback = (tag_name, value) => {
        fetch('http://localhost:8000/links/create-slide-link?' + new URLSearchParams({
            slide_id: selectedSlide.id,
            tag_name: tag_name,
            value: value
        }),{
            method: 'POST',
            credentials: 'include'
        })
    }

    const removeSlideTagCallback = (tag_name) => {
        fetch('http://localhost:8000/links/remove-slide-link?' + new URLSearchParams({
            slide_id: selectedSlide.id,
            tag_name: tag_name,
        }),{
            method: 'POST',
            credentials: 'include'
        })
    }

    useEffect(() => {
        if (selectedSlide) {
            fetch('http://localhost:8000/links/slide-links?' + new URLSearchParams({
                slide_id: selectedSlide.id
            }),{
                credentials: 'include'
            }).then(res => res.json()).then(((data) => tagTableRef.current.updateTable(data.links)))
        }

    }, [selectedSlide])

    useEffect(() => {
        if (selectedPresentation) {
            setSelectedSlide(null)
            fetch('http://localhost:8000/slides/by-pres-id?' +
                new URLSearchParams({ pres_id: selectedPresentation.id }),
                { credentials: "include" }
            ).then(res => res.json()).then(data => setSelectedPresentationSlides(data.slides))
        }
    }, [selectedPresentation])

    useEffect(() => {
        if (props.userFileTree === null) {
            setProcessedUserFileTree(null)
        }
    }, [props.userFileTree])

    useEffect(() => {
        (async () => {
            if (props.userFileTree !== null && showSelectPresentation) {
                const userFileTreeCopy = Object.assign({}, props.userFileTree)
                let filteredPresentations = null

                if (searchMode === 'tags') {
                    filteredPresentations = await fetch("http://localhost:8000/presentations/by-tag-query?" +
                        new URLSearchParams({query: searchFieldValue}), {credentials: "include"}
                    ).then(res => res.json()).then(data => data.filtered_presentations)
                }

                const traverse = (node) => {
                    if (node.type === 'folder') {
                        node.menuObjectType = MenuObjectType.FOLDER
                        const result = node.children.map(child => traverse(child))
                        node.show = node.mark && result.some(child => child)
                        return node.show
                    } else {
                        node.menuObjectType = MenuObjectType.PRESENTATION
                        if (props.created.includes(node.id)) {
                            node.status = 'created'
                        } else if (props.modified.includes(node.id)) {
                            node.status = 'modified'
                        } else {
                            node.status = 'default'
                        }
                        switch (searchMode) {
                            case 'name':
                                node.show = node.name.includes(searchFieldValue)
                                return node.name.includes(searchFieldValue)
                            case 'tags':
                                if (filteredPresentations) {
                                    node.show = filteredPresentations.map(pres => pres.id).includes(node.id)
                                } else {
                                    node.show = true
                                }
                                return node.show
                        }

                    }
                }

                traverse(userFileTreeCopy)

                userFileTreeCopy.menuObjectType = MenuObjectType.ROOT_FOLDER
                userFileTreeCopy.show = true

                setProcessedUserFileTree(userFileTreeCopy)

                return () => {}
            }
        })()
    }, [props.userFileTree, showSelectPresentation, searchFieldValue, searchMode, props.created, props.modified])


    return (
        <div className='TagView'>
            <div className='toolbar'>
                <button
                    onMouseEnter={() => setShowSelectPresentation(true)}
                    onMouseLeave={() => setShowSelectPresentation(false)}
                >
                    Открыть презентацию
                    {showSelectPresentation ?
                        <SelectPresentationMenu
                            ref={selectPresentationMenuRef}
                            processedUserFileTree={processedUserFileTree}
                            setShowSelectPresentation={setShowSelectPresentation}
                            setSelectedPresentation={setSelectedPresentation}
                            searchFieldValue={searchFieldValue}
                            setSearchFieldValue={setSearchFieldValue}
                            searchMode={searchMode}
                            setSearchMode={setSearchMode}
                            updateFiles={props.updateFiles}
                        /> : null}
                </button>
                <button onClick={() => setShowPresentationTags(true)}>Теги презентации</button>
            </div>
            <div className='body'>
                <div className='pres-view'>
                    {selectedPresentation ? <div className='pres-name'>{selectedPresentation.name}</div> : null}
                    {selectedPresentationSlides.length > 0 ?
                        selectedPresentationSlides.map(slideObj =>
                            <SlideCard
                                slide={slideObj}
                                selectedSlide={selectedSlide}
                                setSelectedSlide={setSelectedSlide}/>)
                        :
                        null
                    }
                </div>
                <div className='slide-view'>
                    {selectedSlide ? <SlideCard slide={selectedSlide} expand={true}/> : null}
                </div>
                <div className='tag-info'>
                    {selectedSlide ?
                        <TagTable
                            ref={tagTableRef}
                            createTagCallback={createSlideTagCallback}
                            updateTagCallback={createSlideTagCallback}
                            removeTagCallback={removeSlideTagCallback}
                        /> : null
                    }
                </div>
            </div>
            {showPresentationTags ? <PresentationTagsModal
                setShowPresentationTags={setShowPresentationTags}
                selectedPresentation={selectedPresentation}
            /> : null}
        </div>
    )
}


export default TagView