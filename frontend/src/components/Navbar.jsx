export default function Navbar()
{
    return(
        <div className="navbar">
            <div className="menu navbar-menu">
                <h4>Menu</h4>
                <button className="nav nav-dashboard">
                    <span className="material-symbols-outlined icon">dashboard</span>
                    <span>Dashboard</span>
                </button>
                <button className="nav nav-statistics">
                    <span className="material-symbols-outlined icon">leaderboard </span>
                    <span>Statistics</span>
                </button>
                <button className="nav nav-wallet">
                    <span className="material-symbols-outlined icon">account_balance_wallet</span>
                    <span>Wallet</span>
                </button>
            </div>

            <div className="menu navbar-more">
                <h4>More</h4>       
                <button className="nav nav-logout">
                    <span className="material-symbols-outlined icon">logout</span>
                    <span>Log out</span>
                </button>
            </div>
        </div>
    )
}