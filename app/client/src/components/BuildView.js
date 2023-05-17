import React, {useEffect, useState} from 'react'
import './BuildView.css'
import SlidePoolBlock from "./SlidePoolBlock";
import PresentationPreviewBlock from "./PresentationPreviewBlock";

import ImportSlidesModal from "./ImportSlidesModal";
import BuildPresentationModal from "./BuildPresentationModal";
import SelectFolderModal from "./SelectFolderModal";
import moveAllIcon from '../icons/export-all.svg'
import moveSelectedIcon from '../icons/export-selected.svg'

const BuildView = (props) => {
    const [poolSlides, setPoolSlides] = useState([])
    const [selectedPoolSlides, setSelectedPoolSlides] = useState([])
    const [previewSlides, setPreviewSlides] = useState([])

    const moveAll = () => {
        setPreviewSlides(prev => [...prev, ...poolSlides])
    }

    const moveSelected = () => {
        setPreviewSlides(prev => [...prev, ...selectedPoolSlides])
        setSelectedPoolSlides([])
    }


    const [showImportSlides, setShowImportSlides] = useState(false)
    const [showBuildPresentation, setShowBuildPresentation] = useState(false)

    return (
        <div className='BuildView'>
            <div className='toolbar'>
                <button onClick={() => setShowImportSlides(true)}>Импорт слайдов</button>
                <button onClick={() => setShowBuildPresentation(true)}>Собрать презентацию</button>
            </div>
            <div className='body'>
                <SlidePoolBlock poolSlides={poolSlides} selectedPoolSlides={selectedPoolSlides} setSelectedPoolSlides={setSelectedPoolSlides}/>
                <div className='controls'>
                    <button onClick={moveAll}>
                        <img src={moveAllIcon}/>
                    </button>
                    <button onClick={moveSelected}>
                        <img src={moveSelectedIcon}/>
                    </button>
                </div>
                <PresentationPreviewBlock previewSlides={previewSlides} setPreviewSlides={setPreviewSlides}/>
            </div>

            {showImportSlides ?
                <ImportSlidesModal
                    userFileTree={props.userFileTree}
                    setShowImportSlides={setShowImportSlides}
                    setPoolSlides={setPoolSlides}
                    setSelectedPoolSlides={setSelectedPoolSlides}
                /> : null
            }
            {showBuildPresentation ?
                <BuildPresentationModal
                    userFileTree={props.userFileTree}
                    showBuildPresentation={showBuildPresentation}
                    setShowBuildPresentation={setShowBuildPresentation}
                    previewSlides={previewSlides}
                /> : null
            }
        </div>
    )
}

export default BuildView