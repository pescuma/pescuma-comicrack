import clr
clr.AddReference('System')
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')

import System.Drawing
import System.Windows.Forms

from System.Drawing import *
from System.Windows.Forms import *

from _utils import *


_allIssueFields = set([ 
	'AddedTime',
	'AgeRating',
	'AlternateCaption',
	'AlternateCount',
	'AlternateNumber',
	'AlternateSeries',
	'ArtistInfo',
	'BlackAndWhite',
	'BookmarkCount',
	'Caption',
	'CaptionWithoutFormat',
	'CaptionWithoutTitle',
	'Characters',
	'Colorist',
	'CommunityRating',
	'Count',
	'Cover',
	'CoverArtist',
	'CurrentPage',
	'CurrentPageInfo',
	'Date',
	'Editor',
	'FileCreationTime',
	'FileDirectory',
	'FileFormat',
	'FileIsMissing',
	'FileLocation',
	'FileModifiedTime',
	'FileName',
	'FileNameWithExtension',
	'FilePath',
	'FileSize',
	'Format',
	'FrontCoverCount',
	'FrontCoverPageIndex',
	'FullAlternateName',
	'FullAlternateNumber',
	'FullName',
	'FullNumber',
	'FullPublisher',
	'FullSeries',
	'Genre',
	'Imprint',
	'InfoText',
	'Inker',
	'LastPageRead',
	'Letterer',
	'Locations',
	'Manga',
	'Month',
	'Notes',
	'Number',
	'OpenedCount',
	'OpenedTime',
	'PageCount',
	'Penciller',
	'Published',
	'Publisher',
	'Rating',
	'ReadPercentage',
	'Series',
	'Status',
	'Summary',
	'Tags',
	'Teams',
	'Title',
	'Volume',
	'Web',
	'Writer',
	'Year'
	])
_allSeriesFields = set([ 
	'Name',
	'FullName',
	'Cover',
	'NumIssues',
	'Issues',
	'MissingIssues',
	'DuplicatedIssues',
	'ReadPercentage',
	'FilesFormat',
	'Rating',
	'CommunityRating',
	'FullPublishers',
	'Publishers',
	'Imprints',
	'Format',
	'NextIssuesToRead'
	])


def _FixFields(fs, possibilities):
	ret = []
	for f in fs:
		if f == '-' or f in possibilities:
			ret.append(f)
	return ret

def FixIssueFields(fs):
	return _FixFields(fs, _allIssueFields)

def FixSeriesFields(fs):
	return _FixFields(fs, _allSeriesFields)
	

class Field:
	def __init__(self, id):
		self.id = id
		self.name = Translate(id)
	
	def __str__(self):
		return self.name


class OptionsForm(Form):
	def __init__(self, skins, config):
		self._skins = skins
		self._config = config.copy()
		self.InitializeComponent()
		self.PopulateFields()
		
	def InitializeComponent(self):
		self._skinLabel = System.Windows.Forms.Label()
		self._skinCombo = System.Windows.Forms.ComboBox()
		self._seriesFieldsLabel = System.Windows.Forms.Label()
		self._issueFieldsLabel = System.Windows.Forms.Label()
		self._seriesFields = System.Windows.Forms.CheckedListBox()
		self._issueFields = System.Windows.Forms.CheckedListBox()
		self._seriesAddSeparator = System.Windows.Forms.Button()
		self._issueAddSeparator = System.Windows.Forms.Button()
		self._okButton = System.Windows.Forms.Button()
		self._cancelButton = System.Windows.Forms.Button()
		self._seriesUp = System.Windows.Forms.Button()
		self._seriesDown = System.Windows.Forms.Button()
		self._issueDown = System.Windows.Forms.Button()
		self._issueUp = System.Windows.Forms.Button()
		self._seriesHideEmptyFields = System.Windows.Forms.CheckBox()
		self._issuesHideEmptyFields = System.Windows.Forms.CheckBox()
		self._issuesNumberOfFirstPagesLabel = System.Windows.Forms.Label()
		self._issuesNumberOfFirstPages = System.Windows.Forms.NumericUpDown()
		self._slowDownWarning = System.Windows.Forms.Label()
		self._issuesNumberOfFirstPages.BeginInit()
		self.SuspendLayout()
		# 
		# skinLabel
		# 
		self._skinLabel.Location = System.Drawing.Point(14, 16)
		self._skinLabel.Name = "skinLabel"
		self._skinLabel.Size = System.Drawing.Size(45, 18)
		self._skinLabel.TabIndex = 0
		self._skinLabel.Text = Translate("Options.Skin", "Skin:")
		# 
		# skinCombo
		# 
		self._skinCombo.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
		self._skinCombo.FormattingEnabled = True
		self._skinCombo.Location = System.Drawing.Point(65, 13)
		self._skinCombo.Name = "skinCombo"
		self._skinCombo.Size = System.Drawing.Size(162, 21)
		self._skinCombo.Sorted = True
		self._skinCombo.TabIndex = 1
		self._skinCombo.SelectedIndexChanged += self.SkinComboSelectedIndexChanged
		# 
		# seriesFieldsLabel
		# 
		self._seriesFieldsLabel.Location = System.Drawing.Point(13, 53)
		self._seriesFieldsLabel.Name = "seriesFieldsLabel"
		self._seriesFieldsLabel.Size = System.Drawing.Size(100, 19)
		self._seriesFieldsLabel.TabIndex = 2
		self._seriesFieldsLabel.Text = Translate("Options.SerieFields", "Serie fields:")
		# 
		# issueFieldsLabel
		# 
		self._issueFieldsLabel.Location = System.Drawing.Point(183, 53)
		self._issueFieldsLabel.Name = "issueFieldsLabel"
		self._issueFieldsLabel.Size = System.Drawing.Size(100, 23)
		self._issueFieldsLabel.TabIndex = 8
		self._issueFieldsLabel.Text = Translate("Options.IssueFields", "Issue fields:")
		# 
		# seriesFields
		# 
		self._seriesFields.FormattingEnabled = True
		self._seriesFields.Location = System.Drawing.Point(13, 76)
		self._seriesFields.Name = "seriesFields"
		self._seriesFields.Size = System.Drawing.Size(155, 169)
		self._seriesFields.TabIndex = 3
		# 
		# issueFields
		# 
		self._issueFields.FormattingEnabled = True
		self._issueFields.Location = System.Drawing.Point(184, 76)
		self._issueFields.Name = "issueFields"
		self._issueFields.Size = System.Drawing.Size(156, 169)
		self._issueFields.TabIndex = 9
		# 
		# seriesAddSeparator
		# 
		self._seriesAddSeparator.FlatAppearance.BorderColor = System.Drawing.SystemColors.Control
		self._seriesAddSeparator.FlatStyle = System.Windows.Forms.FlatStyle.Popup
		self._seriesAddSeparator.Location = System.Drawing.Point(13, 244)
		self._seriesAddSeparator.Name = "seriesAddSeparator"
		self._seriesAddSeparator.Size = System.Drawing.Size(155, 23)
		self._seriesAddSeparator.TabIndex = 4
		self._seriesAddSeparator.Text = Translate("Options.AddSeparator", "Add Separator")
		self._seriesAddSeparator.UseVisualStyleBackColor = True
		self._seriesAddSeparator.Click += self.SerieAddSeparatorClick
		# 
		# issueAddSeparator
		# 
		self._issueAddSeparator.FlatStyle = System.Windows.Forms.FlatStyle.Popup
		self._issueAddSeparator.Location = System.Drawing.Point(184, 244)
		self._issueAddSeparator.Name = "issueAddSeparator"
		self._issueAddSeparator.Size = System.Drawing.Size(156, 23)
		self._issueAddSeparator.TabIndex = 10
		self._issueAddSeparator.Text = Translate("Options.AddSeparator", "Add Separator")
		self._issueAddSeparator.UseVisualStyleBackColor = True
		self._issueAddSeparator.Click += self.IssueAddSeparatorClick
		# 
		# okButton
		# 
		self._okButton.DialogResult = System.Windows.Forms.DialogResult.OK
		self._okButton.Location = System.Drawing.Point(182, 374)
		self._okButton.Name = "okButton"
		self._okButton.Size = System.Drawing.Size(75, 23)
		self._okButton.TabIndex = 17
		self._okButton.Text = Translate("Options.OK", "OK")
		self._okButton.UseVisualStyleBackColor = True
		self._okButton.Click += self.OkButtonClick
		# 
		# cancelButton
		# 
		self._cancelButton.DialogResult = System.Windows.Forms.DialogResult.Cancel
		self._cancelButton.Location = System.Drawing.Point(264, 373)
		self._cancelButton.Name = "cancelButton"
		self._cancelButton.Size = System.Drawing.Size(75, 23)
		self._cancelButton.TabIndex = 18
		self._cancelButton.Text = Translate("Options.Cancel", "Cancel")
		self._cancelButton.UseVisualStyleBackColor = True
		# 
		# seriesUp
		# 
		self._seriesUp.FlatStyle = System.Windows.Forms.FlatStyle.Popup
		self._seriesUp.Location = System.Drawing.Point(13, 266)
		self._seriesUp.Name = "seriesUp"
		self._seriesUp.Size = System.Drawing.Size(78, 23)
		self._seriesUp.TabIndex = 5
		self._seriesUp.Text = Translate("Options.Up", "Up")
		self._seriesUp.UseVisualStyleBackColor = True
		self._seriesUp.Click += self.SeriesUpClick
		# 
		# seriesDown
		# 
		self._seriesDown.FlatStyle = System.Windows.Forms.FlatStyle.Popup
		self._seriesDown.Location = System.Drawing.Point(89, 266)
		self._seriesDown.Name = "seriesDown"
		self._seriesDown.Size = System.Drawing.Size(79, 23)
		self._seriesDown.TabIndex = 6
		self._seriesDown.Text = Translate("Options.Down", "Down")
		self._seriesDown.UseVisualStyleBackColor = True
		self._seriesDown.Click += self.SeriesDownClick
		# 
		# issueDown
		# 
		self._issueDown.FlatStyle = System.Windows.Forms.FlatStyle.Popup
		self._issueDown.Location = System.Drawing.Point(261, 266)
		self._issueDown.Name = "issueDown"
		self._issueDown.Size = System.Drawing.Size(79, 23)
		self._issueDown.TabIndex = 12
		self._issueDown.Text = Translate("Options.Down", "Down")
		self._issueDown.UseVisualStyleBackColor = True
		self._issueDown.Click += self.IssueDownClick
		# 
		# issueUp
		# 
		self._issueUp.FlatStyle = System.Windows.Forms.FlatStyle.Popup
		self._issueUp.Location = System.Drawing.Point(184, 266)
		self._issueUp.Name = "issueUp"
		self._issueUp.Size = System.Drawing.Size(78, 23)
		self._issueUp.TabIndex = 11
		self._issueUp.Text = Translate("Options.Up", "Up")
		self._issueUp.UseVisualStyleBackColor = True
		self._issueUp.Click += self.IssueUpClick
		# 
		# seriesHideEmptyFields
		# 
		self._seriesHideEmptyFields.Location = System.Drawing.Point(14, 295)
		self._seriesHideEmptyFields.Name = "seriesHideEmptyFields"
		self._seriesHideEmptyFields.Size = System.Drawing.Size(156, 22)
		self._seriesHideEmptyFields.TabIndex = 7
		self._seriesHideEmptyFields.Text = Translate("Options.HideEmptyFields", "Hide empty fields")
		self._seriesHideEmptyFields.UseVisualStyleBackColor = True
		# 
		# issuesHideEmptyFields
		# 
		self._issuesHideEmptyFields.Location = System.Drawing.Point(185, 295)
		self._issuesHideEmptyFields.Name = "issuesHideEmptyFields"
		self._issuesHideEmptyFields.Size = System.Drawing.Size(156, 22)
		self._issuesHideEmptyFields.TabIndex = 13
		self._issuesHideEmptyFields.Text = Translate("Options.HideEmptyFields", "Hide empty fields")
		self._issuesHideEmptyFields.UseVisualStyleBackColor = True
		# 
		# issuesNumberOfFirstPagesLabel
		# 
		self._issuesNumberOfFirstPagesLabel.Location = System.Drawing.Point(184, 324)
		self._issuesNumberOfFirstPagesLabel.Name = "issuesNumberOfFirstPagesLabel"
		self._issuesNumberOfFirstPagesLabel.Size = System.Drawing.Size(100, 19)
		self._issuesNumberOfFirstPagesLabel.TabIndex = 14
		self._issuesNumberOfFirstPagesLabel.Text = Translate("Options.NumOfFirstPages", "Num of first pages:")
		# 
		# issuesNumberOfFirstPages
		# 
		self._issuesNumberOfFirstPages.Location = System.Drawing.Point(291, 322)
		self._issuesNumberOfFirstPages.Name = "issuesNumberOfFirstPages"
		self._issuesNumberOfFirstPages.Size = System.Drawing.Size(48, 20)
		self._issuesNumberOfFirstPages.TabIndex = 15
		self._issuesNumberOfFirstPages.Value = System.Decimal(System.Array[System.Int32](
			[0,
			0,
			0,
			0]))
		# 
		# slowDownWarning
		# 
		self._slowDownWarning.Font = System.Drawing.Font("Microsoft Sans Serif", 8.25, System.Drawing.FontStyle.Italic, System.Drawing.GraphicsUnit.Point, 0)
		self._slowDownWarning.Location = System.Drawing.Point(15, 345)
		self._slowDownWarning.Name = "slowDownWarning"
		self._slowDownWarning.Size = System.Drawing.Size(325, 17)
		self._slowDownWarning.TabIndex = 16
		self._slowDownWarning.Text = Translate("Options.FirstPagesSlowDownWarning", "(showing the first pages slows down the script)")
		self._slowDownWarning.TextAlign = System.Drawing.ContentAlignment.TopRight
		# 
		# OptionsForm
		# 
		self.AcceptButton = self._okButton
		self.CancelButton = self._cancelButton
		self.ClientSize = System.Drawing.Size(351, 408)
		self.Controls.Add(self._slowDownWarning)
		self.Controls.Add(self._issuesNumberOfFirstPages)
		self.Controls.Add(self._issuesNumberOfFirstPagesLabel)
		self.Controls.Add(self._issuesHideEmptyFields)
		self.Controls.Add(self._seriesHideEmptyFields)
		self.Controls.Add(self._issueDown)
		self.Controls.Add(self._issueUp)
		self.Controls.Add(self._seriesDown)
		self.Controls.Add(self._seriesUp)
		self.Controls.Add(self._cancelButton)
		self.Controls.Add(self._okButton)
		self.Controls.Add(self._issueAddSeparator)
		self.Controls.Add(self._seriesAddSeparator)
		self.Controls.Add(self._issueFields)
		self.Controls.Add(self._seriesFields)
		self.Controls.Add(self._issueFieldsLabel)
		self.Controls.Add(self._seriesFieldsLabel)
		self.Controls.Add(self._skinCombo)
		self.Controls.Add(self._skinLabel)
		self.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog
		self.MaximizeBox = False
		self.MinimizeBox = False
		self.Name = "OptionsForm"
		self.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent
		self.Text = Translate("Options.Title", "Series Info Panel Options")
		self._issuesNumberOfFirstPages.EndInit()
		self.ResumeLayout(False)
	
	def PopulateFields(self):
		self._issuesNumberOfFirstPages.BeginInit()
		self.SuspendLayout()
		
		_skin = None
		self._skinCombo.Items.Clear()
		for skin in self._skins.values():
			self._skinCombo.Items.Add(skin)
			if skin.id == self._config.skin:
				_skin = skin
		self._skinCombo.SelectedItem = _skin
		
		self._seriesFieldsLabel.Enabled = _skin.canEditFields
		self._issueFieldsLabel.Enabled = _skin.canEditFields
		self._issueFields.Enabled = _skin.canEditFields
		self._seriesFields.Enabled = _skin.canEditFields
		self._seriesAddSeparator.Enabled = _skin.canEditFields
		self._issueAddSeparator.Enabled = _skin.canEditFields
		self._seriesUp.Enabled = _skin.canEditFields
		self._seriesDown.Enabled = _skin.canEditFields
		self._issueDown.Enabled = _skin.canEditFields
		self._issueUp.Enabled = _skin.canEditFields
		self._seriesHideEmptyFields.Enabled = _skin.canEditFields
		self._issuesHideEmptyFields.Enabled = _skin.canEditFields
		
		if skin.canEditFields:
			self.PopulateIssues(self._issueFields, self._config.issueFields, set(_allIssueFields))
			self.PopulateIssues(self._seriesFields, self._config.seriesFields, set(_allSeriesFields))
			self._seriesHideEmptyFields.Checked = self._config.seriesHideEmptyFields
			self._issuesHideEmptyFields.Checked = self._config.issuesHideEmptyFields
		else:
			self._issueFields.Items.Clear()
			self._seriesFields.Items.Clear()
			self._seriesHideEmptyFields.Checked = False
			self._issuesHideEmptyFields.Checked = False
		
		self._issuesNumberOfFirstPages.Value = self._config.issuesNumberOfFirstPages
	
		self._issuesNumberOfFirstPages.EndInit()
		self.ResumeLayout(False)
		
	
	def PopulateIssues(self, ctrl, items, allPosibilities):
		ctrl.Items.Clear()
		
		for i in items:
			if i != '-' and i not in allPosibilities:
				print '[SIP] Ignoring field because it is not avaiable: ' + i
				continue
			
			ctrl.Items.Add(Field(i), True)
			
			allPosibilities.discard(i)
		
		for i in sorted(allPosibilities):
			ctrl.Items.Add(Field(i), False)
			

	def AddSeparatorClick(self, fields):
		pos = fields.SelectedIndex
		if pos < 0:
			pos = fields.Items.Count
		fields.Items.Insert(pos, Field('-'))
		fields.SetItemChecked(pos, True)
		fields.SelectedIndex = pos

	def UpClick(self, fields):
		pos = fields.SelectedIndex
		if pos < 1 or pos >= fields.Items.Count:
			return
		
		tmp = fields.Items[pos]
		fields.Items[pos] = fields.Items[pos-1]
		fields.Items[pos-1] = tmp
		
		tmp = fields.GetItemChecked(pos)
		fields.SetItemChecked(pos, fields.GetItemChecked(pos-1))
		fields.SetItemChecked(pos-1, tmp)
		
		fields.SelectedIndex = pos-1
		
	def DownClick(self, fields):
		pos = fields.SelectedIndex
		if pos < 0 or pos >= fields.Items.Count - 1:
			return
		
		tmp = fields.Items[pos]
		fields.Items[pos] = fields.Items[pos+1]
		fields.Items[pos+1] = tmp
		
		tmp = fields.GetItemChecked(pos)
		fields.SetItemChecked(pos, fields.GetItemChecked(pos+1))
		fields.SetItemChecked(pos+1, tmp)
		
		fields.SelectedIndex = pos+1
	
	def SerieAddSeparatorClick(self, sender, e):
		self.AddSeparatorClick(self._seriesFields)

	def SeriesUpClick(self, sender, e):
		self.UpClick(self._seriesFields)

	def SeriesDownClick(self, sender, e):
		self.DownClick(self._seriesFields)

	def IssueAddSeparatorClick(self, sender, e):
		self.AddSeparatorClick(self._issueFields)

	def IssueUpClick(self, sender, e):
		self.UpClick(self._issueFields)

	def IssueDownClick(self, sender, e):
		self.DownClick(self._issueFields)

	def SkinComboSelectedIndexChanged(self, sender, e):
		skin = self._skinCombo.SelectedItem
		if skin.id == self._config.skin:
			return
		self._config.skin = skin.id
		self._config.seriesFields = skin.seriesFields
		self._config.issueFields = skin.issueFields
		self._config.seriesHideEmptyFields = skin.seriesHideEmptyFields
		self._config.issuesHideEmptyFields = skin.issuesHideEmptyFields
		self._config.issuesNumberOfFirstPages = skin.issuesNumberOfFirstPages
		self.PopulateFields()
	
	def LoadFromCtrl(self, ctrl):
		ret = []
		
		for pos in range(ctrl.Items.Count):
			if not ctrl.GetItemChecked(pos):
				continue
			ret.append(ctrl.Items[pos].id)
		
		return ret
	
	def OkButtonClick(self, sender, e):
		self._config.issueFields = self.LoadFromCtrl(self._issueFields)
		self._config.seriesFields = self.LoadFromCtrl(self._seriesFields)
		self._config.seriesHideEmptyFields = self._seriesHideEmptyFields.Checked
		self._config.issuesHideEmptyFields = self._issuesHideEmptyFields.Checked
		self._config.issuesNumberOfFirstPages = ToInt(self._issuesNumberOfFirstPages.Value)



