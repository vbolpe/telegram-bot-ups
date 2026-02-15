def format_status(data: dict) -> str:
    if not data:
        return "No se pudo obtener el estado de la UPS"
    
    return(
        f"Estado UPS\n\n"
        f"Estado: {data['status']}\n"
        f"Bateria: {data.get('baterry', 'N/A')}%\n"
        f"Carga: {data.get('load', 'N/A')}%\n"
        f"Última actualización: {data['last_update']}"
    )

def format_event(event: dict) -> str:
    if not event:
        return None
    
    return(
        f" Cambio de estado UPS \n\n"
        f"Anterior: {event['old']}\n"
        f"Actual: {event['new']}\n"
        f"Fecha: {event['timestamp']}"
    )