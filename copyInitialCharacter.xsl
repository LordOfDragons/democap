<?xml version='1.0' encoding='UTF-8' ?>
<xsl:transform version='1.0'
xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
xmlns:dcc='http://dragondreams.ch/democap/character'
exclude-result-prefixes='dcc'>
	<xsl:output method='xml' encoding='UTF-8'/>
	
	<!-- skip calibration tags -->
	<xsl:template match="inputDevice">
		<inputDevice/>
	</xsl:template>
	
	<xsl:template match="calibrated">
		<calibrated/>
	</xsl:template>
	
	<xsl:template match="transfers">
		<transfers/>
	</xsl:template>
	
	<!--
	<xsl:template match="reachScalingArmRight">
		<reachScalingArmRight x='1' y='1' z='1'/>
	</xsl:template>
	
	<xsl:template match="reachScalingArmRightBack">
		<reachScalingArmRightBack x='1' y='1' z='1'/>
	</xsl:template>
	
	<xsl:template match="reachScalingArmLeft">
		<reachScalingArmLeft x='1' y='1' z='1'/>
	</xsl:template>
	
	<xsl:template match="reachScalingArmLeftBack">
		<reachScalingArmLeftBack x='1' y='1' z='1'/>
	</xsl:template>
	-->
	
	<!-- copy all tags and attributes -->
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>
</xsl:transform>
