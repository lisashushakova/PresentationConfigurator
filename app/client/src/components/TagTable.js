import './TagTable.css'
import {useEffect, useRef, useState} from "react";
import greenPlusIcon from '../icons/plus-green.svg';
import redCrossIcon from '../icons/cross-red.svg';
import greenCheckIcon from '../icons/check-green.svg';
import React from 'react'

const TableCreateTagRow = (props) => {
    const CreateTagRowState = {
        DEFAULT: 0,
        ABLE_TO_CREATE: 1,
    }

    const [rowState, setRowState] = useState(CreateTagRowState.DEFAULT)

    const [tagName, setTagName] = useState('')
    const [tagValue, setTagValue] = useState('')

    const tagNameRef = React.createRef()

    useEffect(() => {
        setTagName('')
        setTagValue('')
        if (tagNameRef.current) {
            tagNameRef.current.classList.remove('error')
        }
    }, [props.rows])

    return (
        <div className='TableCreateTagRow'>
            <input ref={tagNameRef} value={tagName} type='text' placeholder='tag' onChange={(e) => {
                setTagName(e.target.value)

                if (!/^[a-zа-яA-ZА-Я]+[a-zа-яA-ZА-Я0-9]*$/.test(e.target.value)) {
                    e.target.classList.add('error')
                } else {
                    e.target.classList.remove('error')
                }

                if (/^[a-zA-Z]+[a-zA-Z0-9]*$/.test(e.target.value) && /^[0-9]*$/.test(tagValue)) {
                    setRowState(CreateTagRowState.ABLE_TO_CREATE)
                } else {
                    setRowState(CreateTagRowState.DEFAULT)
                }

            }}/>
            <input value={tagValue} type='text' placeholder='100' onChange={(e) => {
                setTagValue(e.target.value)

                if (!/^[0-9]*$/.test(e.target.value)) {
                    e.target.classList.add('error')
                } else {
                    e.target.classList.remove('error')
                }

                if (/^[a-zA-Z]+[a-zA-Z0-9]*$/.test(tagName) && /^[0-9]*$/.test(e.target.value)) {
                    setRowState(CreateTagRowState.ABLE_TO_CREATE)
                } else {
                    setRowState(CreateTagRowState.DEFAULT)
                }

            }}/>
            {rowState === CreateTagRowState.ABLE_TO_CREATE ? <button><img src={greenPlusIcon} onClick={() => {
                props.createCallback(tagName, tagValue, tagNameRef)
            }}/></button> : null}
        </div>
    )
}

const TableRow = (props) => {
    const TableRowState = {
        DEFAULT: 0,
        UNSAVED_CHANGES: 1,
    }

    const [rowState, setRowState] = useState(TableRowState.DEFAULT)
    const [inputState, setInputState] = useState('')
    const [tagValue, setTagValue] = useState(props.tagValue)

    const removeBtn = <button onClick={() => {
        props.removeCallback(props.tagName)
    }}><img src={redCrossIcon}/></button>

    const saveChangesBtn = <button className='save-changes-btn' onClick={(e) => {
        setTagValue(inputState)
        setRowState(TableRowState.DEFAULT)
        props.updateTagCallback(props.tagName, inputState)
    }}>
        <img src={greenCheckIcon}/>
    </button>

    return (<div className='TableRow'>
            <div>{props.tagName}</div>
            <input
                type='text'
                defaultValue={props.tagValue}
                onChange={(e) => {
                    setInputState(e.target.value)
                    if (!/^[0-9]*$/.test(e.target.value)) {
                        e.target.classList.add('error')
                        setRowState(TableRowState.DEFAULT)
                    } else {
                        e.target.classList.remove('error')
                        if (tagValue !== e.target.value) {
                            setRowState(TableRowState.UNSAVED_CHANGES)
                        } else {
                            setRowState(TableRowState.DEFAULT)
                        }
                    }
                }}
                onBlur={(e) => {
                    if (!(e.relatedTarget && e.relatedTarget.className === 'save-changes-btn')) {
                        e.target.value = tagValue
                        e.target.classList.remove('error')
                        setRowState(TableRowState.DEFAULT)
                    }

                }}
                />
            {rowState === TableRowState.DEFAULT ? removeBtn : saveChangesBtn}
        </div>)
}

class TagTable extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            rows: []
        }

        this.createCallback = (tagName, tagValue, tagInput) => {
            const tagsWithSameName = this.state.rows.filter(el => el.props.tagName === tagName)
            if (tagsWithSameName.length === 0) {
                this.setState({rows: [...this.state.rows,
                    <TableRow
                        key={tagName}
                        tagName={tagName}
                        tagValue={tagValue}
                        removeCallback={this.removeCallback}
                        updateTagCallback={this.props.createTagCallback}
                    />
                    ]})
                this.props.createTagCallback(tagName, tagValue)
            } else {
                tagInput.current.classList.add('error')
            }

        }

        this.removeCallback = (tagName) => {
            this.setState({rows: this.state.rows.filter(el => el.props.tagName !== tagName)})
            this.props.removeTagCallback(tagName)
        }
    }

    updateTable(tagsWithValue) {
        let newRows = []
        for (const tagWithValue of tagsWithValue) {
            newRows.push(<TableRow
                key={tagWithValue.tag_name}
                tagName={tagWithValue.tag_name}
                tagValue={tagWithValue.value}
                removeCallback={this.removeCallback}
                updateTagCallback={this.props.createTagCallback}
            />)
        }
        this.setState({rows: newRows})
    }


    render() {
        return (<div className='TagTable'>
            <div className='table-header'>
                <div>Тег</div>
                <div>Значение</div>
            </div>
            <TableCreateTagRow createCallback={this.createCallback} rows={this.state.rows}/>
                <div className='tag-row-wrapper'>
                    <div className='scroller'>
                        {this.state.rows}
                    </div>
                </div>
        </div>)
    }



}


export default TagTable