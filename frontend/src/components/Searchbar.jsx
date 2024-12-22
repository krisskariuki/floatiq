export default function Searchbar()
{
    return(
        <div className="searchbar">
            <span className="material-symbols-outlined center-child search-icon">search</span>

            <input type="text" id="search-input" placeholder='search here...'/>
        </div>
    )
}