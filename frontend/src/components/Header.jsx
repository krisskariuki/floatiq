import Logo from './Logo'
import Searchbar from './Searchbar'
import Dp from './Dp'

export default function Header()
{
    return(
        <section className="header">
            <Logo logoInfo={{url:'/imgs/logo.png',alt:'description picture'}}/>
            <Searchbar/>
            <div className="dynamic-island"></div>

            <div className="account-info">
                <span class="user-name" >John doe</span>
                <span className="user-tel">0112345678</span>
            <Dp dpInfo={{url:'/imgs/dp.png',alt:'description picture'}}/>
            </div>
        </section>
    )
}