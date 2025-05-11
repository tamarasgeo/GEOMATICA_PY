# -*- coding: utf-8 -*-
"""
TWI - TAMARA SEPÚLVEDA
"""

import os
import numpy as np
import richdem as rd
import matplotlib.pyplot as plt
from osgeo import gdal

def mostrar_estadisticas(array, nombre):
    """MUESTRA ESTADÍSTICAS"""
    print(f"\nEstadísticas para {nombre}:")
    print(f"- Dimensión: {array.shape}")
    print(f"- Mínimo: {np.nanmin(array):.4f}")
    print(f"- Máximo: {np.nanmax(array):.4f}")
    print(f"- Media: {np.nanmean(array):.4f}")
    print(f"- Desviación estándar: {np.nanstd(array):.4f}")

def visualizacion_basica(array, nombre, cmap='viridis'):
    """VISUALIZACIÓN BÁSICA"""
    plt.figure(figsize=(10, 6))
    plt.imshow(array, cmap=cmap)
    plt.colorbar(label='Valor')
    plt.title(nombre)
    plt.axis('off')
    plt.show()

def calcular_twi_con_analisis():
    """FLUJO PRINCIPAL"""
    # RUTAS
    input_dir = r"C:\GEO\EJEMPLO_TWI"
    dem_path = os.path.join(input_dir, "DEMPICHI.tif")
    output_dir = input_dir
    
    try:
        # VISUALIZACIÓN INTERACTIVA
        plt.ion()  # ACTIVA MODO INTERACTIVO
        
        # CARGA DEM
        dem = rd.LoadGDAL(dem_path)
        print("DEM cargado correctamente")
        mostrar_estadisticas(dem, "DEM Original")
        visualizacion_basica(dem, "DEM Original", cmap='terrain')
        
        # FILL DEM
        dem_filled = rd.FillDepressions(dem)
        rd.SaveGDAL(os.path.join(output_dir, "DEM_FILLED.tif"), dem_filled)
        mostrar_estadisticas(dem_filled, "DEM Rellenado")
        visualizacion_basica(dem_filled, "DEM Rellenado", cmap='terrain')
        
        # SLOPE
        slope = rd.TerrainAttribute(dem_filled, attrib='slope_radians')
        rd.SaveGDAL(os.path.join(output_dir, "SLOPE.tif"), slope)
        mostrar_estadisticas(slope, "Pendiente (radianes)")
        visualizacion_basica(slope, "Pendiente (radianes)", cmap='magma')
        
        # FLOW ACCUMULATION
        flow_accum = rd.FlowAccumulation(dem_filled, method='D8')
        rd.SaveGDAL(os.path.join(output_dir, "FLOW_ACC.tif"), flow_accum)
        mostrar_estadisticas(flow_accum, "Acumulación de Flujo")
        
        # ESCALA LOGARÍTMICA
        flow_accum_log = np.log1p(flow_accum)
        visualizacion_basica(flow_accum_log, "Acumulación de Flujo (log)", cmap='Blues')
        
        # TWI
        cell_size = abs(dem.geotransform[1])
        sca = flow_accum * cell_size
        slope_safe = np.maximum(slope, 0.001)
        sca_safe = np.maximum(sca, 0.001)
        twi = np.log(sca_safe / np.tan(slope_safe))
        rd.SaveGDAL(os.path.join(output_dir, "TWI_RESULT.tif"), twi)
        
        # MUESTRA ESTADÍSTICAS TWI
        print("\nRESULTADOS FINALES TWI:")
        mostrar_estadisticas(twi, "Índice TWI")
        
        # VISUALIZA TWI CON RANGO TÍPICO
        plt.figure(figsize=(10, 6))
        plt.imshow(twi, cmap='viridis', vmin=5, vmax=20)
        plt.colorbar(label='Valor TWI')
        plt.title("Índice Topográfico de Humedad (TWI)\nValores típicos: 5-20")
        plt.axis('off')
        plt.show()
        
        print("\nProceso completado. Archivos guardados en:", output_dir)
        
    except Exception as e:
        print(f"\nError durante el procesamiento: {str(e)}")
    finally:
        plt.ioff()  # DESACTIVA MODO INTERACTIVO AL FINAL

if __name__ == "__main__":
    # CONFIGURA ENTORNO
    if 'CONDA_PREFIX' in os.environ:
        os.environ['PATH'] = os.path.join(os.environ['CONDA_PREFIX'], 'Library', 'bin') + ';' + os.environ['PATH']
    
    calcular_twi_con_analisis()