import { WorkshopShell, type WorkshopLocale } from "./WorkshopShell";
type Props={locale?:WorkshopLocale;alternateHref:string;contactHref?:string;showReach?:boolean;light?:boolean;children:React.ReactNode};
export function WorkshopEditorial({locale="ru",alternateHref,contactHref,showReach=true,light=false,children}:Props){
  return <WorkshopShell locale={locale} alternateHref={alternateHref} contactHref={contactHref} showReach={showReach} light={light}>{children}</WorkshopShell>;
}
