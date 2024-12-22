export default function Logo({logoInfo})
{
    return(
        <img src={logoInfo.url} alt={logoInfo.alt} className="logo" />
    )
}