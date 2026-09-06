import { WorkshopShell, type WorkshopLocale } from "./WorkshopShell";
type Props={locale?:WorkshopLocale;alternateHref:string;contactHref?:string;children:React.ReactNode};
export function WorkshopEditorial({locale="ru",alternateHref,contactHref,children}:Props){
  return <WorkshopShell locale={locale} alternateHref={alternateHref} contactHref={contactHref}>{children}</WorkshopShell>;
}
