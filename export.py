'''
Created on 6 Apr 2021

@author: thomasgumbricht
'''

import os

import numpy as np

import subprocess

from geoimagine.layout import ProcessLayout

import geoimagine.support.karttur_dt as mj_dt

class ProcessExport():
    '''class for modis specific processing'''
      
    def __init__(self, pp, session):
        '''
        '''
                
        self.session = session
                
        self.pp = pp  
        
        self.verbose = self.pp.process.verbose 
        
        self.session._SetVerbosity(self.verbose)
        
        print ('        ProcessExport', self.pp.process.processid) 
        
        if self.pp.process.parameters.asscript:
            
            today = mj_dt.Today()
            
            scriptFP = os.path.join('/Volumes',self.pp.dstPath.volume, self.pp.procsys.dstsystem, 'export-pilot')
            
            if not os.path.exists(scriptFP):
                
                os.makedirs(scriptFP)
                
            scriptFN = 'export-pilot_%(today)s.sh' %{'today':today}
            
            scriptFPN = os.path.join(scriptFP,scriptFN)
            
            self.pilotScriptF = open(scriptFPN,'a+')
            
            writeln = '# Pilot script created by Kartturs GeoImagine Framework for Export processing, created %s\n' %(today)
    
            self.pilotScriptF.write(writeln)
            
        #direct to subprocess
                  
        if 'movieclock' in self.pp.process.processid.lower():
            
            self._MovieClock()
            
            if self.pp.process.parameters.asscript and self.framecriptF:
                
                print ('        run',self.framescriptFPN)
                
                print ('        run',self.moviescriptFPN)
                
                exit('Exiting - you now have to run the shell scripts above')
                
            return
        
        #Set scriptF to False, if asscript == True, self.scriptF gets a value furhter down
        self.scriptF = False
        
        if 'movieframe' in self.pp.process.processid.lower() and self.pp.process.parameters.asscript:
            
            self._IniMovieFrameScript()
            
        if 'movieoverlayframe' in self.pp.process.processid.lower():
            
            self._IniMovieFrameScript()
            
        self._LoopAllLayers()
        
        if 'movieframe' in self.pp.process.processid.lower() and self.scriptF:
            
            self.scriptF.close()
            
            print ('        run',self.scriptFPN)
            
        if 'movieoverlayframe' in self.pp.process.processid.lower() and self.scriptF:
            
            self.scriptF.close()
            
            print ('        run',self.scriptFPN)
            
        printstr = '    Finished ProcessExport: %(s)s' %{'s':self.pp.process.processid}
        
        print (printstr)
        
        if self.pp.process.parameters.asscript:
            
            self.pilotScriptF.close()
            
            infostr = 'Run the pilot script file:\n    %s' %(scriptFPN)
            
            print (infostr)
        
        
    def _LoopAllLayers(self):
        '''
        '''
        
        if self.pp.process.parameters.asscript:
            
            today = mj_dt.Today()
            
            scriptFP = os.path.join('/Volumes',self.pp.dstPath.volume, self.pp.procsys.dstsystem, self.pp.dstCompD[self.pp.dstCompL[0]].source,'export')
            
            if not os.path.exists(scriptFP):
                
                os.makedirs(scriptFP)
                
            scriptFN = 'export_%(compid)s-%(today)s.sh' %{'compid':self.pp.dstCompD[self.pp.dstCompL[0]].compid, 'today':today}
            
            scriptFPN = os.path.join(scriptFP,scriptFN)
            
            self.exportScriptF = open(scriptFPN,'w')
            
            writeln = '# Script created by Kartturs GeoImagine Framework for Export processing, created %s\n' %(today)
    
            self.exportScriptF.write(writeln)
            
            cmd = 'chmod 755 %s\n%s\n' %(scriptFPN, scriptFPN)
            
            self.pilotScriptF.write(cmd)
                    
        
        for locus in self.pp.srcLayerD:
            
            for datum in self.pp.srcPeriod.datumL:
                                           
                for comp in self.pp.srcLayerD[locus][datum]:
                                    
                    srcLayer = self.pp.srcLayerD[locus][datum][comp]
                    
                    if not os.path.exists(srcLayer.FPN):
                        
                        infostr = '    SKIPPING - input layer missing for ProcessExport\n        %s' %(srcLayer.FPN)
            
                        print (infostr)
                        
                        continue
                    
                                        
                    if 'ziparchive' in self.pp.process.processid.lower():
                        
                        self._ArchiveIni(locus,datum,comp)
                        
                    elif 'duplicate' in self.pp.process.processid.lower():
                        
                        self._DuplicateIni(locus,datum,comp)
                        
                    elif self.pp.process.processid.lower() == 'exporttilestobyte':
                        
                        self._ExportToByte(locus,datum,comp)
                        
                    elif self.pp.process.processid.lower() == 'exportshadedtilestobyte':
                        
                        self._ExportShadedToByte(locus,datum,comp)
                        
                    
                        
                        
                        
                    elif not self.pp.dstLayerD[locus][datum][comp]._Exists() or self.pp.process.overwrite:
                        
                        if 'append' in self.pp.process.processid.lower():
                            
                            self._MovieAppendFrames(locus,datum,comp)
                            
                        elif 'movieframe' in self.pp.process.processid.lower():
                            
                            self._MovieFrames(locus,datum,comp)
                            
                        elif 'movieoverlayframe' in self.pp.process.processid.lower():
                            
                            self._MovieOverlayFrames(locus,datum)
                            
                        elif 'exporttosvg' in self.pp.process.processid.lower():
                            
                            self._ExportSVG(srclocus,dstlocus,datum,srcCompL[0],dstcomp)
                            
                        elif 'exportmap' in self.pp.process.processid.lower():
                        
                            self._ExportMap(locus,datum,comp)
                            
                        else:
                            
                            exitstr = 'EXITING - unrecognize export command in ProcessExport: %s' %(self.pp.process.processid)
           
                            exit(exitstr)
           
        if self.pp.process.parameters.asscript:
            
            self.exportScriptF.close()
            
            infostr = 'To render the commands, run the script file:\n    %s' %(scriptFPN)
            
            print (infostr)
            
    def _ExportToByte(self,locus,datum,comp):
        '''
        '''
    
        self._SelectScaling(comp)
            
        self._SetPalette(comp)
        
        if not self.pp.dstLayerD[locus][datum][comp]._Exists() or self.pp.process.overwrite:
            
            self._ExportLayer(locus,datum,comp)
            
        self._CreateMainLayout(locus,datum,comp)
        
        #self._CreateDetailLayout(locus, datum, comp)
                           
    def _ExportShadedToByte(self,locus,datum,comp):
        '''
        '''
  
        # Create shading if not already done
          
        if not self.pp.dstLayerD[locus]['0']['shade']._Exists() or self.pp.process.overwriteshade:
                    
            print ('        Creating shading for location %s\n        %s' %(locus, self.pp.dstLayerD[locus]['0']['shade'].FPN) )
                                
            self._SelectScaling('shade')
            
            self._SetPalette('shade')
            
            self._ExportLayer(locus,'0','shade')
            
            self.pp.process.overwriteshade = False
            
            self._ShadeMagickLayout(locus, datum, comp)
        
        if comp == 'shade':
            
            # if the layout is for shade itself, return
            
            return
        
        self.shadeFPN = self.pp.dstLayerD[locus]['0']['shade'].FPN.replace( self.pp.dstLayerD[locus][datum][comp].comp.ext,'.png')
        
        self._SelectScaling(comp)
            
        self._SetPalette(comp)
        
        if not self.pp.dstLayerD[locus][datum][comp]._Exists() or self.pp.process.overwrite:
            
            self._ExportLayer(locus,datum,comp)
                                    
        self._CreateShadedLayout(locus, datum, comp)
                                                       
    def _ExportMap(self,locus,datum,comp):
        '''
        '''
        #self.SetMask()
        

        if not self.pp.dstLayerD[locus][datum][comp]._Exists() or self.pp.process.overwrite:
            
            self._SelectScaling(comp)

            self._SelectLegend(comp)
            
            measure = self.process.proc.dstcompD[comp]['measure']
            
            self._SetPalette(comp)
            
            mapArr = self._ExportLayer(locus,datum,comp, True)

            MapPlot(mapArr, self.process, self.process.dstCompD[comp].colorRamp, self.legend, self.scaling, measure, self.process.srcLayerD[locus][datum][comp], self.pp.dstLayerD[locus][datum][comp])
      
    def _SelectLegend(self,comp):
        '''THIS IS A DUPLICATE FROM layout.legend
        Select legend from database
        '''
        legendD = self.session.IniSelectLegend(self.pp.process.dstcompD[comp])

        self.legend = lambda: None
        
        for key, value in legendD.items():
            
            setattr(self.legend, key, value)
            
        self.legend.frame = int(self.legend.framestrokewidth+0.99)
        
    def _SelectScaling(self,comp):
        '''
        '''

        scalingD = self.session.IniSelectScaling(self.pp.dstCompD[comp])
        
        self.scaling = lambda: None 
        
        for key, value in scalingD.items():
        
            setattr(self.scaling, key, value)
               
    def _SetPalette(self,comp):
        ''' Palette set in paramjson at startup (from 5 Apr 2021)
        '''
        pass

    def _ExportLayer(self,locus,datum,comp,returnmap=False):
        '''
        '''
        
        self.legendFPN = False
        
        #Open the src layer
        self.pp.srcLayerD[locus][datum][comp].RasterOpenGetFirstLayer()
        
        self.pp.srcLayerD[locus][datum][comp].layer.ReadBand()
                    
        if self.pp.process.parameters.zscore and comp != 'shade':
            
            origBAND = self.pp.srcLayerD[locus][datum][comp].layer.NPBAND
            
            srcBAND = np.copy(origBAND)
            
            if self.pp.process.parameters.globalstd:
                
                std = self.pp.process.parameters.globalstd
                
            else:
                
                std = np.std(srcBAND )
                
            if self.pp.process.parameters.globalmean:
                
                mean = self.pp.process.parameters.globalmean
                
            else:
                
                mean = np.mean( srcBAND )
                
            srcBAND = ( srcBAND - mean) / std
            
            srcBAND *= self.pp.process.parameters.zscorefac
            
        else:  
            
            srcBAND = self.pp.srcLayerD[locus][datum][comp].layer.NPBAND
        
        srcCellNull = self.pp.srcLayerD[locus][datum][comp].layer.cellnull
        
        if comp == 'shade':
            
            dstBAND = srcBAND
            
        else:
            
            if self.pp.process.parameters.minmax:
                
                self.scaling.log = self.scaling.power = 0 
                
                if self.pp.process.parameters.srcmin == self.pp.process.parameters.srcmax:
                
                    srcmin = np.amin(srcBAND)
                    
                    srcmax = np.amax(srcBAND)
                                          
                else:
                    
                    srcmin = self.pp.process.parameters.srcmin
                    
                    srcmax = self.pp.process.parameters.srcmax
                                        
                scalefac = 1.0/((srcmax-srcmin)/250.0)
                    
                offsetadd = srcmin*scalefac
                
                if self.pp.process.parameters.detaillegend:
                    
                    self._CreateLegend(srcmin,srcmax,scalefac,offsetadd,locus,comp)
                    
            else:
                
                scalefac = self.scaling.scalefac
                
                offsetadd = self.scaling.offsetadd
            
            if self.scaling.power:
                                 
                if self.scaling.mirror0:
                    
                    BAND = srcBAND
                    dstBANDIni = np.power(BAND, self.scaling.power)
                    dstBANDIni *=  self.scaling.scalefac
                    dstBANDInv = np.power(-BAND, self.scaling.power)
                    dstBANDInv *= - self.scaling.scalefac
                    MASK = (BAND < 0)
                    dstBAND = np.copy(dstBANDIni)
                    dstBAND[MASK] = dstBANDInv[MASK]
                    dstBAND += 125
                else:
                    #changed to work with VWB deficit 20181125
                    BAND = srcBAND
                    dstBANDIni = np.power(BAND, self.scaling.power)
                    dstBANDIni *=  scalefac
                    #dstBANDInv = np.power(-BAND, self.scaling.power)
                    #dstBANDInv *= - self.scaling.scalefac
                    #MASK = (BAND < 0)
                    dstBAND = np.copy(dstBANDIni)
                    #dstBAND[MASK] = dstBANDInv[MASK]
                    dstBAND += offsetadd
                    
            elif self.scaling.log:
                # natural logarithm             
                BAND = srcBAND
                
                dstBAND = np.log(BAND)
                
                dstBAND *=  scalefac
                   
                dstBAND += offsetadd
                    
            elif self.scaling.mirror0 or self.scaling.offsetadd == 125: 
                
                dstBAND =  srcBAND * scalefac
                
                dstBAND += 125
                
            else:  
                #Only scale and offset
                
                dstBAND = srcBAND*scalefac
                
                dstBAND += offsetadd

        dstBAND[dstBAND < 0] = 0
            
        dstBAND[dstBAND > 250] = 250

        #set null to 255
        dstBAND[srcBAND == srcCellNull] = 255
        
        #set nan to 255
        dstBAND[np.isnan(srcBAND)] = 255
        
        if returnmap:
            return dstBAND
        
        #Create the dst layer
        
        self.pp.dstLayerD[locus][datum][comp].layer = lambda:None
        
        #Set the np array as the band
        
        self.pp.dstLayerD[locus][datum][comp].layer.NPBAND = dstBAND
        
        #copy the geoformat from the src layer
        
        self.pp.dstLayerD[locus][datum][comp].CopyGeoformatFromSrcLayer(self.pp.srcLayerD[locus][datum][comp].layer)
        
        self.pp.dstLayerD[locus][datum][comp].comp.celltype = 'Byte'
        
        self.pp.dstLayerD[locus][datum][comp].comp.cellnull = 255
        
        #Create the dst layer
        self.pp.dstLayerD[locus][datum][comp].RasterCreateWithFirstLayer()  
        
    def _LayoutTitle(self,locus,datum,comp):
        
        compD = {'prefix':self.pp.dstLayerD[locus][datum][comp].comp.prefix,
                 'suffix':self.pp.dstLayerD[locus][datum][comp].comp.suffix,
                 'content':self.pp.dstLayerD[locus][datum][comp].comp.content,
                 'source':self.pp.dstLayerD[locus][datum][comp].comp.source,
                 'product':self.pp.dstLayerD[locus][datum][comp].comp.product,
                 'datum':datum,
                 'loucs':locus}
        
        title = self.pp.process.parameters.title %compD
                        
        titleD = {'bkgcolor': self.pp.process.parameters.titlebackgroundcolor,
                  'font':self.pp.process.parameters.titlefont, 'size':self.pp.process.parameters.titlefontsize,
                  'fill':self.pp.process.parameters.titlefontcolor, 'gravity':self.pp.process.parameters.titlegravity,
                  'title':title}
        
        # see https://stackoverflow.com/questions/58621445/imagemagick-how-to-create-an-annotation-that-would-fit-its-size-into-any-image
        
        if self.pp.process.parameters.titlesingleline:
            
            titleD['mode'] = 'label'
        
        else:
            
            titleD['mode'] = 'caption'
            
        return '\( -background %(bkgcolor)s -bordercolor %(bkgcolor)s -font %(font)s -pointsize %(size)d -fill "%(fill)s" -gravity %(gravity)s %(mode)s:"%(title)s" -virtual-pixel background -distort SRT "0.8 0" -virtual-pixel none -distort SRT "0.8 0" \) -composite ' %titleD
    
    def _LayoutLegend(self,locus,datum,comp):
        
        if self.legendFPN:
            
            legendFPN = self.legendFPN
            
        else:
                
            compid = self.pp.dstLayerD[locus][datum][comp].comp.compid
            
            legendFP = os.path.join('/Volumes',self.pp.process.dstpath.volume,'legends','svg')
            
            
            
            legendFN = '%s_%s.png' %(compid, self.pp.process.parameters.palette)
            
            legendFPN = os.path.join(legendFP,legendFN)
        
        if not os.path.exists(legendFPN):
            
            infostr = 'WARNING legend %s not found, skipping legend' %(legendFPN)
            
            print (infostr)
            
            return False
        
        legendD = {'bkgcolor':self.pp.process.parameters.detaillegendbackground,  
                   'legendFPN':legendFPN, 'gravity':self.pp.process.parameters.detaillegendgravity}
            
        return '\( -background %(bkgcolor)s -gravity %(gravity)s %(legendFPN)s \) -composite ' %legendD


    def _CreateLegend(self,srcmin,srcmax,scalefac,offsetadd,locus,comp):
        '''
        '''

        # Get the legend entries for the selected palette
        
        layout = ProcessLayout(self.pp, self.session)
        
        layout.scaling = lambda:None
        
        layout.scaling.offsetadd = -offsetadd
        
        layout.scaling.scalefac = 1.0/scalefac
        
        layout.scaling.power = layout.scaling.log = 0
        
        layout.imgD = {}
        
        #Export each composition (if several)
        # Convert the parameters to a dict 
        #queryD = dict( list( self.pp.process.parameters.__dict__.items() ) )
        
        #for comp in self.pp.srcCompD:
            
        compD = dict( list( self.pp.dstCompD[comp].__dict__.items() ) )
            
        layout.compid = compD['compid']
                        
        #Create the target paths
        layout.pngFP = os.path.join('/Volumes',self.pp.process.dstpath.volume,'legendsauto',locus,'png')
            
        layout.pdfFP = os.path.join('/Volumes',self.pp.process.dstpath.volume,'legendsauto',locus,'pdf')
            
        layout.svgFP = os.path.join('/Volumes',self.pp.process.dstpath.volume,'legendsauto',locus,'svg')
            
        if not os.path.exists(layout.pngFP):
                
            os.makedirs(layout.pngFP)
                
        if not os.path.exists(layout.pdfFP):
                
            os.makedirs(layout.pdfFP)
                
        if not os.path.exists(layout.svgFP):
                
            os.makedirs(layout.svgFP)
                
        # Set the filenames  
        layout.svgFN = '%s_%s.svg' %(layout.compid, self.pp.process.parameters.palette)
            
        layout.svgFPN = os.path.join(layout.svgFP,layout.svgFN)
            
        self.legendFPN = layout.pngFPN = layout.svgFPN.replace('.svg','.png')
            
        layout.jpgFPN = layout.svgFPN.replace('.svg','.jpg')
            
        if not self.pp.process.overwrite:
            
            if os.path.exists(layout.svgFPN) and os.path.exists(layout.pngFPN):
                    
                if not self.pp.process.parameters.jpg or os.path.exists(self.jpgFPN):
                        
                    return
                
        #Get the measure (i.e. O,R,I)
        layout._SelectCompFormat()
            
        #Get the scaling
        #self._SelectScaling(comp)
            
        #Get the legend
        layout._SelectLegend(comp)
            
        #Get the palette
        layout._SelectPaletteColors()
                    
        #Set the legend dimensions
        layout._SetLegendDim()

        layout._CreateFramesOIR()
            
        layout._WriteLegendImgs()
                                     
        layout._ConstructSVG()
          
    def _CreateMainLayout(self,locus,datum,comp):
        '''
        '''
        
        FPN = self.pp.dstLayerD[locus][datum][comp].FPN
            
        pngFPN = FPN.replace(self.pp.dstLayerD[locus][datum][comp].comp.ext,'.png')
        
        if not os.path.exists(pngFPN) or self.pp.process.overwrite  or self.pp.process.parameters.overwritelayout:
            
            cropL = self._SetCropDims(self.pp.process.parameters.crop)
                    
            width = self.pp.process.parameters.width
            
            if not cropL and not width:
                
                return
            
            border = self.pp.process.parameters.border
            
            bordercolor = self.pp.process.parameters.bordercolor
            
            if len(self.pp.process.parameters.vectoroverlay) > 4:
                
                if os.path.isfile(self.pp.process.parameters.vectoroverlay):
                    
                    overlay = self.pp.process.parameters.vectoroverlay
                    
                else:
                    
                    exit('The vectoroverlay for movieframes does not exist')
                    
            else:
                
                overlay = False
                
            embossptsize = self.pp.process.parameters.embossptsize
                
            if len(self.pp.process.parameters.emboss) > 0:
                
                emboss = True
                
            else:
                
                emboss = False
                  
            embdimL = self.pp.process.parameters.embossdims.split(',')
                
            if len(embdimL) == 2:
                
                embdimL = [int(item) for item in embdimL]
                    
            else:
                    
                embdimL = False
                
            if self.pp.process.parameters.detaillegend:
                
                legend = self._LayoutLegend(locus,datum,comp)
                
            else:
                
                legend = False
                
            if hasattr(self.pp.process.parameters, 'title') and self.pp.process.parameters.title:
                
                title = self._LayoutTitle(locus,datum,comp)
                
            else:
                
                title = False
                
            self._MagickPng(FPN, pngFPN, cropL, width, border, bordercolor, overlay, emboss, embdimL, embossptsize, title, legend)

        if self.pp.process.parameters.jpg:
        
            jpgFPN = FPN.replace(self.pp.dstLayerD[locus][datum][comp].comp.ext,'.jpg') 
        
            if not os.path.exists(jpgFPN) or self.pp.process.overwrite: 
                
                self._MagickPngToJpg(pngFPN, jpgFPN, self.pp.process.parameters.jpg)
                
                
    def _ShadeMagickLayout(self,locus,datum,comp):
        '''
        '''
        
        FPN = self.pp.dstLayerD[locus][datum][comp].FPN
            
        self.shadeFPN = FPN.replace(self.pp.dstLayerD[locus][datum][comp].comp.ext,'.png')
        
        if self.verbose:
            
            print ('        shadeFPN',self.shadeFPN)
        
        if os.path.exists(self.shadeFPN) and not self.pp.process.overwrite:
            
            return
        
        iniFN = 'initial-hillshade.png'
        
        dblFN = 'double-hillshade.png'
        
        whtFN = 'white-hillshade.png'
        
        alphaFN = 'alpha-hillshade.png'
        
        iniFPN = os.path.join(os.path.split(self.shadeFPN)[0],iniFN)
        
        dblFPN = os.path.join(os.path.split(self.shadeFPN)[0],dblFN)
        
        whtFPN = os.path.join(os.path.split(self.shadeFPN)[0],whtFN)
        
        alphaFPN = os.path.join(os.path.split(self.shadeFPN)[0],alphaFN)
        
        paramsD ={'src': FPN,'dst':self.shadeFPN,'ini':iniFPN,'dbl':dblFPN, 'wht':whtFPN, 'alf':alphaFPN}
        
        paramsD['alphashade'] = self.pp.process.parameters.alphashade
        
        paramsD['fuzzalpha'] = self.pp.process.parameters.fuzzalpha
        
        #paramsD['doubleshade'] = self.pp.process.parameters.doubleshadow
        
        #paramsD['bumpshade'] = self.pp.process.parameters.bump
        

        

        
 
        
        if self.pp.process.parameters.shadefactor > 1:
            
            shdFPN = dblFPN
        
        else:
            
            shdFPN = iniFPN
                        
        paramsD['shd'] = shdFPN
        
        # Get the cropping    
        cropL = self._SetCropDims(self.pp.process.parameters.crop)
           
        width = self.pp.process.parameters.width
        
        if not cropL and not width:
            
            return
        
        ####
            
        if cropL:
            
            paramsD['w'] = cropL[0]; paramsD['h'] = cropL[1]
            
            paramsD['cw'], paramsD['ch'],paramsD['cx'],paramsD['cy'] = cropL
            
            magickCmd = 'convert \( -crop %(cw)dx%(ch)d+%(cx)d+%(cy)d %(src)s \) ' %paramsD
            
            if width:
                    
                paramsD['w'] = width
                
                magickCmd += ' \( -resize %(w)dx %(src)s \) -composite ' %paramsD
                   
                #if shadealpha: 
                    
                #magickCmd += ' \( -resize %(w)dx %(shade)s -alpha on -channel a -evaluate set %(alpha)d%% \) -composite ' %paramsD
                #magickCmd += ' \( -crop %(cw)dx%(ch)d+%(cx)d+%(cy)d %(shade)s -alpha on -channel a -evaluate set %(alpha)d%% \) -composite ' %paramsD

        elif width:
        
            paramsD['w'] = width
            
            magickCmd = 'convert \( -resize %(w)dx %(src)s \)' %paramsD
            
        magickCmd += '%(ini)s' %paramsD 
        
        if self.verbose > 1:
            
            print ('        ',magickCmd)  
        
        subprocess.call('/usr/local/bin/' + magickCmd, shell=True)
        
        if self.pp.process.parameters.shadefactor > 1:
            
            # Increase shadow
            
            magickCmd = 'composite -compose Multiply %(ini)s %(ini)s %(dbl)s' %paramsD
            
            if self.verbose > 1:
            
                print ('        ',magickCmd)
                
            subprocess.call('/usr/local/bin/' + magickCmd, shell=True)
            
            factor = 2
                
            while True:
                
                if factor >= self.pp.process.parameters.shadefactor:
                    
                    break
                    
                magickCmd = 'composite -compose Multiply %(dbl)s %(ini)s %(dbl)s' %paramsD
                
                if self.verbose > 1:
                
                    print ('        ',magickCmd)

                subprocess.call('/usr/local/bin/' + magickCmd, shell=True) 
                
                factor *= 2
             
        # Whitening
 
        magickCmd = 'convert \( -size "%(w)d x %(h)d" canvas:none  -fill "#c0c0c0" -draw "rectangle 0,0,%(w)d,%(h)d" \) ' %paramsD
        
        magickCmd += '%(shd)s -compose Divide -composite %(wht)s' %paramsD  
        
        if self.verbose > 1:
            
            print ('        ',magickCmd)
                  
        subprocess.call('/usr/local/bin/' + magickCmd, shell=True) 
        
        # Set hillshape alpha
        magickCmd = 'convert %(wht)s -channel RGBA -matte -fill none -fuzz %(fuzzalpha)s%% -opaque "#c0c0c0" %(dst)s'  %paramsD 
                
        if self.verbose > 1:
            
            print ('        ',magickCmd)
  
        subprocess.call('/usr/local/bin/' + magickCmd, shell=True)
        
        if paramsD['bumpshade']:
          
            pass
            # To implement see: https://en.wikipedia.org/wiki/Wikipedia:Graphic_Lab/Resources/Creating_shaded_relief_(GDAL,_ImageMagick)
                                       
    def _CreateShadedLayout(self, locus, datum, comp):
        '''Create a layout and export to PNG
        '''
        
        FPN = self.pp.dstLayerD[locus][datum][comp].FPN
            
        pngFPN = FPN.replace(self.pp.dstLayerD[locus][datum][comp].comp.ext,'.png')
        
        if not os.path.exists(pngFPN) or self.pp.process.overwrite  or self.pp.process.parameters.overwriteshade:
            
            cropL = self._SetCropDims(self.pp.process.parameters.crop)
                    
            width = self.pp.process.parameters.width
            
            if not cropL and not width:
                
                return
            
            border = self.pp.process.parameters.border
            
            bordercolor = self.pp.process.parameters.bordercolor
            
            if len(self.pp.process.parameters.vectoroverlay) > 4:
                
                if os.path.isfile(self.pp.process.parameters.vectoroverlay):
                    
                    overlay = self.pp.process.parameters.vectoroverlay
                    
                else:
                    
                    exit('The vectoroverlay for movieframes does not exist')
                    
            else:
                
                overlay = False
                
            embossptsize = self.pp.process.parameters.embossptsize
                
            if len(self.pp.process.parameters.emboss) > 0:
                
                emboss = True
                
            else:
                
                emboss = False
                  
            embdimL = self.pp.process.parameters.embossdims.split(',')
                
            if len(embdimL) == 2:
                
                embdimL = [int(item) for item in embdimL]
                    
            else:
                    
                embdimL = False
                
                
            if self.pp.process.parameters.detaillegend:
                
                legend = self._LayoutLegend(locus,datum,comp)
                
            else:
                
                legend = False
                
            if hasattr(self.pp.process.parameters, 'title') and self.pp.process.parameters.title:
                
                title = self._LayoutTitle(locus,datum,comp)
                
            else:
                
                title = False
                
            alpha = int(self.pp.process.parameters.alphashade*100)
   
            self._MagickPng(FPN, pngFPN, cropL, width, border, bordercolor, overlay, emboss, embdimL, embossptsize, title, legend, alpha )

        if self.pp.process.parameters.jpg:
        
            jpgFPN = FPN.replace(self.pp.dstLayerD[locus][datum][comp].comp.ext,'.jpg') 
        
            if not os.path.exists(jpgFPN) or self.pp.process.overwrite: 
                
                self._MagickPngToJpg(pngFPN, jpgFPN, self.pp.process.parameters.jpg)
             
             
                                        
    def _CreateDetailLayout(self,locus,datum,comp,pngMainFPN):
        '''
        '''
        
        pngFPN = pngMainFPN.replace(".png", "-detail.png")
                 
        if not os.path.exists(pngFPN) or self.pp.process.overwrite  or self.pp.process.parameters.overwritelayout:
            
            cropL = self._SetCropDims(self.pp.process.parameters.detailcrop)
                    
            width = self.pp.process.parameters.detailcrop
            
            if not cropL or not width or cropL[0] <= width:
                
                SNULLE
                return
            
            border = self.pp.process.parameters.detailborder
            
            bordercolor = self.pp.process.parameters.detailbordercolor
            
            if len(self.pp.process.parameters.vectoroverlay) > 4:
                
                if os.path.isfile(self.pp.process.parameters.vectoroverlay):
                    
                    overlay = self.pp.process.parameters.vectoroverlay
                    
                else:
                    
                    exit('The vectoroverlay for movieframes does not exist')
                    
            else:
                
                overlay = False
                
            embossptsize = self.pp.process.parameters.embossptsize
                
            if len(self.pp.process.parameters.emboss) > 0:
                
                emboss = True
                
            else:
                
                emboss = False
                  
            embdimL = self.pp.process.parameters.embossdims.split(',')
                
            if len(embdimL) == 2:
                
                embdimL = [int(item) for item in embdimL]
                    
            else:
                    
                embdimL = False
                
            if hasattr(self.pp.process.parameters, 'title') and self.pp.process.parameters.title:
                
                title = self._LayoutTitle(self,locus,datum,comp)
                
            else:
                
                title = False
                
            self._MagickPng(cropL, width, border, bordercolor, overlay, emboss, embdimL, embossptsize, legend, title)

        if self.pp.process.parameters.jpg:
        
            jpgFPN = pngFPN.replace(self.pp.dstLayerD[locus][datum][comp].comp.ext,'.jpg') 
        
            if not os.path.exists(jpgFPN) or self.pp.process.overwrite or self.pp.process.parameters.overwritelayout: 
                
                self._MagickPngToJpg(pngFPN, jpgFPN, self.pp.process.parameters.jpg)       
            
    def _MagickPng(self, srcFPN, dstFPN, cropL, width, border, bordercolor, overlay, emboss, embdimL, embossptsize, title, legend, alphashade=0):
        '''ImageMagick command for writing png
        '''

        paramsD ={'src': srcFPN,'dst':dstFPN}
        
        if alphashade:
                    
            paramsD['shade'] = self.shadeFPN

            paramsD['alphashade'] = alphashade
        
        if cropL:
            
            paramsD['cw'], paramsD['ch'],paramsD['cx'],paramsD['cy'] = cropL
            
            magickCmd = 'convert \( -crop %(cw)dx%(ch)d+%(cx)d+%(cy)d %(src)s \) ' %paramsD
            
            if width:
                    
                paramsD['w'] = width
                
                magickCmd += ' \( -resize %(w)dx %(src)s \) -composite ' %paramsD
                                    
        elif width:
        
            paramsD['w'] = width
            
            magickCmd = 'convert \( -resize %(w)dx %(src)s \)' %paramsD
            
        # Shading
        if alphashade:
            
            # Create an intermediat layer
            
            tmpFPN = dstFPN.replace('.png','-unshaded.png')
            
            paramsD['tmp'] = tmpFPN
            
            magickCmd += '%(tmp)s' %paramsD
        
            if self.verbose > 1:
                
                print ('        ',magickCmd)
                                           
            subprocess.call('/usr/local/bin/' + magickCmd, shell=True)
            
            magickCmd = 'convert \( %(tmp)s \) \( %(shade)s \) -composite ' %paramsD
            
            magickCmd += ' \( %(tmp)s -alpha on -channel a -evaluate set %(alphashade)d%% \) -composite ' %paramsD
                                             
        if overlay:
            
            NOTUNDERSTOOD
            if cropL:
                
                magickCmd += '\( -background none -resize %(cw)dx%(ch)d! %(o)s \) -composite ' %paramsD
            
            else:
            
                magickCmd += '\( -background none -resize %(w)dx %(o)s \) -composite ' %paramsD
        
        if emboss and embdimL:
                        
            paramsD['emboss'] = emboss 
            
            paramsD['ptsize'] = embossptsize

            paramsD['embx'], paramsD['emby'] = embdimL
            
            magickCmd += '\( -size %(embx)dx%(emby)s xc:none -font Trebuchet -pointsize %(ptsize)s -gravity center -draw "fill silver text 1,1 ' %paramsD
            
            magickCmd += "'%(emboss)s' fill whitesmoke text -1,-1 '%(emboss)s' fill grey text 0,0 '%(emboss)s' " %paramsD
            
            magickCmd += '" -transparent grey -fuzz 90%% \) -composite ' %paramsD

        if title:
                         
            magickCmd += title
            
        if legend:
            
            magickCmd += legend
            
        if border:
            
            paramsD['b'] = border
        
            paramsD['bc'] = bordercolor
            
            magickCmd += '\( -border %(b)dx%(b)d -bordercolor %(bc)s \) ' %paramsD
            
        magickCmd += '%(dst)s' %paramsD
        
        if self.verbose > 1:
            
            print ('        ',magickCmd)
            
        subprocess.call('/usr/local/bin/' + magickCmd, shell=True)
        
    def _MagickPngToJpg(self, pngFPN, jpgFPN, jpgquality):
        '''
        '''
        
        paramsD = {'src':pngFPN, 'dst':jpgFPN, 'q':jpgquality}
            
        magickCmd = 'convert %(src)s -quality %(q)d %(dst)s ' %paramsD
            
        subprocess.call('/usr/local/bin/' + magickCmd, shell=True)
        
    def _SetCropDims(self, crop):
        '''
        '''
        
        if crop:
        
            cropL = crop.split(',')
                
            cropL = [int(item) for item in cropL]
            
        else:
                
            cropL = False
            
        return (cropL)
    
    
    def _DuplicateIni(self,locus,datum,comp):
        '''
        '''

        if not self.pp.dstLayerD[locus][datum][comp]._Exists() or self.pp.process.overwrite:
            
            if self.verbose:
            
                infostr = '        Duplicating %s to\n            %s' %(self.pp.srcLayerD[locus][datum][comp].FPN,self.pp.dstLayerD[locus][datum][comp].FPN)
                
                print (infostr)
            
            cmd = 'cp %(src)s %(dst)s' %{'src':self.pp.srcLayerD[locus][datum][comp].FPN,
                                            'dst':self.pp.dstLayerD[locus][datum][comp].FPN}  
                    
            if self.pp.process.parameters.asscript:
                
                cmd += '\n'
                   
                self.exportScriptF.write(cmd)  
                
            else:        
            
                os.system(cmd)
            
    def _ArchiveIni(self,locus,datum,comp):
        '''
        '''

        if not self.pp.dstLayerD[locus][datum][comp]._Exists() or self.pp.process.overwrite:
            
            if self.verbose:
            
                infostr = '        Archiving %s to\n            %s' %(self.pp.srcLayerD[locus][datum][comp].FPN,self.pp.dstLayerD[locus][datum][comp].FPN)
                
                print (infostr)
            
            if self.pp.dstLayerD[locus][datum][comp].comp.ext == '.zip':
                
                self._ArchiveZip(locus,datum,comp)
            
            elif self.pp.dstLayerD[locus][datum][comp].comp.ext == '.gz':
            
                self._archiveGunZip(locus,datum,comp)
            
            elif self.pp.dstLayerD[locus][datum][comp].comp.ext == '.tar':
            
                self._archiveTar(locus,datum,comp)
            
            elif self.pp.dstLayerD[locus][datum][comp].comp.ext == '.gz.tar':
            
                self._archiveGunZipTar(locus,datum,comp)
                
            elif self.pp.dstLayerD[locus][datum][comp].comp.ext == '.tar.gz':
            
                self._archiveTarGunZip(locus,datum,comp)
                
            else:
                
                print (self.pp.dstLayerD[locus][datum][comp].comp.ext)
                
                NOTYETDNE
                
    def _archiveTarGunZip(self,locus,datum,comp):
        '''
        '''
        
        cmd = 'cd %(srcfp)s; '%{'srcfp':self.pp.srcLayerD[locus][datum][comp].FP}
        
        cmd += 'tar -cvzf %(dst)s %(src)s; '  %{'src':self.pp.srcLayerD[locus][datum][comp].FN,
                                            'dst':self.pp.dstLayerD[locus][datum][comp].FN}
        
        cmd+= 'mv %(fn)s %(fpn)s' %{'fn':self.pp.dstLayerD[locus][datum][comp].FN,
                                            'fpn':self.pp.dstLayerD[locus][datum][comp].FPN}  
        
        if self.pp.process.parameters.asscript:
            
            cmd += '\n'
               
            self.exportScriptF.write(cmd)  
            
        else:        
        
            os.system(cmd)