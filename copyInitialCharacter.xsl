<?xml version='1.0' encoding='UTF-8' ?>
<xsl:transform version='1.0'
xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
xmlns='http://dragondreams.ch/democap/character'>
	<xsl:output method='xml' encoding='UTF-8'/>
	
	<!-- skip calibration tags -->
	<xsl:template match="inputDevice"/>
	<xsl:template match="calibrated"/>
	<xsl:template match="transfers"/>
	
	<!-- copy all tags and attributes -->
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>
</xsl:transform>
